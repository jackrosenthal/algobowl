package api

import (
	"gorm.io/gorm"
)

type ServerGlobals struct {
	DbSession *gorm.DB
}
