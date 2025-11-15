SET NAMES 'utf8mb4';
USE ong_sol;

INSERT INTO equipments_type (name) VALUES ('Bengala'), ('Tipóia de joelho'), ('Órtese de pé'), ('Bota ortopédica'), ('Muleta de braço'), ('Colete pequeno'), ('Cadeira de banho'), ('Cadeira de rodas');
INSERT INTO users_role (name) VALUES ('Administrador'), ('Usuário');
INSERT INTO users_user (username, cpf, email, status, create_date, role_id, password) VALUES ('Administrador', '07743623912', 'samuel@rodrigues.social.br', 1, NOW(), 1, 'pbkdf2_sha256$1000000$JVr37EbggxXwtK6NBfraCc$aIvP/vm8k5W/5eivNqJE85x3295AEZx10b/V4LYghRg=');
