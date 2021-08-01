-- upgrade --
CREATE TABLE IF NOT EXISTS "language"
(
    "id" CHAR
(
    36
) NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR
(
    100
) NOT NULL
    );;
CREATE TABLE IF NOT EXISTS "snippet"
(
    "id" CHAR
(
    36
) NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR
(
    200
) NOT NULL,
    "code" TEXT NOT NULL,
    "print_line_number" INT NOT NULL DEFAULT 0,
    "language_id" CHAR
(
    36
) NOT NULL REFERENCES "language"
(
    "id"
) ON DELETE CASCADE,
    "style_id" CHAR
(
    36
) NOT NULL REFERENCES "style"
(
    "id"
)
  ON DELETE CASCADE,
    "user_id" CHAR
(
    36
) NOT NULL REFERENCES "user"
(
    "id"
)
  ON DELETE CASCADE
    );;
CREATE TABLE IF NOT EXISTS "style"
(
    "id" CHAR
(
    36
) NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR
(
    100
) NOT NULL
    );-- downgrade --
DROP TABLE IF EXISTS "language";
DROP TABLE IF EXISTS "snippet";
DROP TABLE IF EXISTS "style";
