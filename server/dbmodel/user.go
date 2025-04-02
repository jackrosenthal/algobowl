package dbmodel

type User struct {
	Id       uint64 `gorm:"primaryKey"`
	Username string
	Email    string
	FullName string
	Admin    bool
}

func (User) TableName() string {
	return "user"
}
