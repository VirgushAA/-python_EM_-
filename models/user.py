from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(ForeignKey("users.id"), primary_key=True)
    role_id = Column(ForeignKey("roles.id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    roles = relationship(
        "Role",
        secondary=UserRole.__table__,
        back_populates="users"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship(
        "User",
        secondary=UserRole.__table__,
        back_populates="roles"
    )

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)  # "post.delete"
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
