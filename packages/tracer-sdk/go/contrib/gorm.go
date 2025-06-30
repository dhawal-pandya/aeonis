package contrib

import (
	"github.com/dhawal-pandya/aeonis/packages/tracer-sdk/go"
	"gorm.io/gorm"
)

type GormTracer struct{}

func (t *GormTracer) Name() string {
	return "gorm:tracer"
}

func (t *GormTracer) Initialize(db *gorm.DB) error {
	cb := db.Callback()
	cb.Create().Before("gorm:create").Register("tracer:before_create", t.before)
	cb.Create().After("gorm:create").Register("tracer:after_create", t.after)
	cb.Query().Before("gorm:query").Register("tracer:before_query", t.before)
	cb.Query().After("gorm:query").Register("tracer:after_query", t.after)
	cb.Update().Before("gorm:update").Register("tracer:before_update", t.before)
	cb.Update().After("gorm:update").Register("tracer:after_update", t.after)
	cb.Delete().Before("gorm:delete").Register("tracer:before_delete", t.before)
	cb.Delete().After("gorm:delete").Register("tracer:after_delete", t.after)
	cb.Row().Before("gorm:row").Register("tracer:before_row", t.before)
	cb.Row().After("gorm:row").Register("tracer:after_row", t.after)
	cb.Raw().Before("gorm:raw").Register("tracer:before_raw", t.before)
	cb.Raw().After("gorm:raw").Register("tracer:after_raw", t.after)
	return nil
}

func (t *GormTracer) before(db *gorm.DB) {
	span, _ := tracer.SpanFromContext(db.Statement.Context)
	if span == nil {
		return
	}
	_, childSpan := span.Tracer().StartSpan(db.Statement.Context, "db.query")
	db.Statement.Context = tracer.ContextWithSpan(db.Statement.Context, childSpan)
}

func (t *GormTracer) after(db *gorm.DB) {
	span, _ := tracer.SpanFromContext(db.Statement.Context)
	if span == nil {
		return
	}
	defer span.End()
	span.SetAttributes(map[string]interface{}{
		"db.statement": db.Statement.SQL.String(),
		"db.vars":      db.Statement.Vars,
		"db.rows_affected": db.RowsAffected,
	})
}
