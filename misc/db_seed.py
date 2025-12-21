from sqlalchemy.orm import Session
from models.user import User, Role, Permission
from core.security import hash_password


def seed_roles_permissions_and_users(db: Session):
    # если уже есть роли. считаем, что база инициализирована
    if db.query(Role).first():
        return

    roles_permissions = {
        "admin": [],
        "moderator": [
            "post.read", "post.update", "post.publish",
            "comment.read", "comment.moderate",
        ],
        "user": [
            "post.read", "post.create",
            "comment.read", "comment.create",
            "order.read", "order.create",
        ],
        "auditor": [
            "user.read", "order.read", "report.read",
        ],
        "guest": [
            "post.read",
        ],
    }

    # ---------- permissions ----------
    perms_map: dict[str, Permission] = {}

    for codes in roles_permissions.values():
        for code in codes:
            if code not in perms_map:
                resource, action = code.split(".")
                perms_map[code] = Permission(
                    code=code,
                    resource=resource,
                    action=action,
                )

    db.add_all(perms_map.values())
    db.commit()

    # ---------- рооли ----------
    roles_map: dict[str, Role] = {}

    all_permissions = list(perms_map.values())

    for role_name, codes in roles_permissions.items():
        role = Role(name=role_name)

        if role_name == "admin":
            role.permissions = all_permissions
        else:
            role.permissions = [perms_map[c] for c in codes]

        roles_map[role_name] = role
        db.add(role)

    db.commit()

    # ---------- users ----------
    users = [
        ("admin@mail.ru", "Admin", "admin"),
        ("moderator@mail.ru", "Moderator", "moderator"),
        ("user@mail.ru", "User", "user"),
        ("auditor@mail.ru", "Auditor", "auditor"),
        ("guest@mail.ru", "Guest", "guest"),
    ]

    password_hash = hash_password("password")

    for email, name, role_name in users:
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            is_active=True,
        )
        user.roles.append(roles_map[role_name])
        db.add(user)

    db.commit()
