-- ============================================================
-- BASE DE DONNÉES – Hôpital Général de Yaoundé 1
-- ============================================================

CREATE DATABASE IF NOT EXISTS hopital_yaounde CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hopital_yaounde;

-- ── Services médicaux ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS services (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  nom   VARCHAR(120) NOT NULL,
  description TEXT
) ENGINE=InnoDB;

-- ── Médecins ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medecins (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nom         VARCHAR(80)  NOT NULL,
  prenom      VARCHAR(80)  NOT NULL,
  specialite  VARCHAR(120) NOT NULL,
  service_id  INT NOT NULL,
  actif       TINYINT(1) DEFAULT 1,
  FOREIGN KEY (service_id) REFERENCES services(id)
) ENGINE=InnoDB;

-- ── Rendez-vous ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rendez_vous (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nom         VARCHAR(80)  NOT NULL,
  prenom      VARCHAR(80)  NOT NULL,
  telephone   VARCHAR(20)  NOT NULL,
  email       VARCHAR(120),
  service_id  INT NOT NULL,
  medecin_id  INT NOT NULL,
  date_rdv    DATE         NOT NULL,
  heure_rdv   TIME         NOT NULL,
  motif       TEXT,
  statut      ENUM('en_attente','confirme','annule') DEFAULT 'en_attente',
  cree_le     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (service_id) REFERENCES services(id),
  FOREIGN KEY (medecin_id) REFERENCES medecins(id)
) ENGINE=InnoDB;

-- ── Données initiales ──────────────────────────────────────
INSERT INTO services (nom, description) VALUES
  ('Médecine Générale',    'Consultations générales et suivi médical'),
  ('Cardiologie',          'Maladies du cœur et des vaisseaux'),
  ('Pédiatrie',            'Soins des enfants de 0 à 15 ans'),
  ('Gynécologie',          'Santé féminine et obstétrique'),
  ('Ophtalmologie',        'Maladies des yeux'),
  ('Chirurgie Générale',   'Interventions chirurgicales'),
  ('Neurologie',           'Maladies du système nerveux'),
  ('Dermatologie',         'Maladies de la peau');

INSERT INTO medecins (nom, prenom, specialite, service_id) VALUES
  ('NKOA',    'Paul',      'Médecin Généraliste',  1),
  ('MBARGA',  'Chantal',   'Médecin Généraliste',  1),
  ('ABOSSOLO','Jacques',   'Cardiologue',          2),
  ('NDAM',    'Florence',  'Cardiologue',          2),
  ('FOUDA',   'Émile',     'Pédiatre',             3),
  ('ONANA',   'Marie-Claire','Pédiatre',           3),
  ('ESSAMA',  'Brigitte',  'Gynécologue',          4),
  ('NGUELE',  'André',     'Gynécologue',          4),
  ('ETOUNDI', 'Laurent',   'Ophtalmologue',        5),
  ('OWONA',   'Suzanne',   'Chirurgien Général',   6),
  ('BELLO',   'Hamidou',   'Neurologue',           7),
  ('TCHUEM',  'Nathalie',  'Dermatologue',         8);

-- ── Utilisateur MySQL pour l'application ──────────────────
-- (Exécuter en tant que root)
-- CREATE USER IF NOT EXISTS 'hopital_user'@'localhost' IDENTIFIED BY 'HopitalYaounde2024!';
-- GRANT ALL PRIVILEGES ON hopital_yaounde.* TO 'hopital_user'@'localhost';
-- FLUSH PRIVILEGES;
