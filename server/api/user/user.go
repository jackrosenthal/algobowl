package user

import (
	"context"

	"connectrpc.com/connect"
	userv1 "github.com/jackrosenthal/algobowl/gen/algobowl/user/v1"
	"github.com/jackrosenthal/algobowl/server/api"
	"github.com/jackrosenthal/algobowl/server/dbmodel"
	"gorm.io/gorm"
)

type UserService struct {
	Globals *api.ServerGlobals
}

func (s *UserService) GetUserInfo(
	ctx context.Context,
	req *connect.Request[userv1.GetUserInfoRequest],
) (*connect.Response[userv1.GetUserInfoResponse], error) {
	var user dbmodel.User
	result := s.Globals.DbSession.Take(&user, "username = ?", req.Msg.Username)
	if result.Error == gorm.ErrRecordNotFound {
		return nil, connect.NewError(connect.CodeNotFound, result.Error)
	}

	if result.Error != nil {
		return nil, connect.NewError(connect.CodeInternal, result.Error)
	}

	return connect.NewResponse(&userv1.GetUserInfoResponse{
		User: &userv1.User{
			Id:          user.Id,
			Username:    user.Username,
			Email:       user.Email,
			DisplayName: user.FullName,
			IsAdmin:     user.Admin,
		},
	}), nil
}
