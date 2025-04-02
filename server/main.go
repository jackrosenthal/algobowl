package main

import (
	"fmt"
	"log/slog"
	"net/http"

	"github.com/alecthomas/kong"
	"github.com/jackrosenthal/algobowl/gen/algobowl/user/v1/userv1connect"
	"github.com/jackrosenthal/algobowl/server/api"
	"github.com/jackrosenthal/algobowl/server/api/user"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"gorm.io/driver/postgres"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var opts struct {
	DbDriver   string `env:"DB_DRIVER" enum:"sqlite,postgres" default:"sqlite" help:"Database driver"`
	DbDsn      string `env:"DB_DSN" default:"file:devdata.db" help:"Database connection string"`
	ListenAddr string `env:"LISTEN_ADDR" default:":8080" help:"Listen address"`
}

func connectToDb(driver string, dsn string) (*gorm.DB, error) {
	var dbCon gorm.Dialector
	switch driver {
	case "sqlite":
		dbCon = sqlite.Open(dsn)
	case "postgres":
		dbCon = postgres.Open(dsn)
	default:
		return nil, fmt.Errorf("unsupported database driver: %s", driver)
	}

	db, err := gorm.Open(dbCon, &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	return db, nil
}

func getServer(globals *api.ServerGlobals) *http.ServeMux {
	mux := http.NewServeMux()
	mux.Handle(userv1connect.NewUserServiceHandler(&user.UserService{Globals: globals}))
	return mux
}

func main() {
	kong.Parse(&opts)
	db, err := connectToDb(opts.DbDriver, opts.DbDsn)
	if err != nil {
		panic(fmt.Errorf("failed to connect to database: %w", err))
	}

	globals := &api.ServerGlobals{
		DbSession: db,
	}
	mux := getServer(globals)

	slog.Info("Server listening", "addr", opts.ListenAddr)
	err = http.ListenAndServe(opts.ListenAddr, h2c.NewHandler(mux, &http2.Server{}))
	panic(err)
}
