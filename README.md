# Projet  :  Application de Rendez-vous dans un hopital de yaoundé

## 👤 Étudiant

- Identifiant : **300138205**
- Nom: Taylor Ngue Ngan
- Cours : Reseau
- Thème : **Mise en evidance de l' automatisation avec ansible🤖**
---


# 🏥 Hôpital Général de Yaoundé 1 – Application de Rendez-vous

Application web Flask pour la prise de rendez-vous médicaux,
déployée automatiquement sur une VM Azure via Ansible.

---

## 📁 Structure du projet

```
hopital-yaounde/
├── app/
│   ├── app.py                  ← Application Flask (routes + logique)
│   ├── requirements.txt        ← Dépendances Python
│   ├── schema.sql              ← Schéma MySQL + données initiales
│   └── templates/
│       ├── base.html           ← Template de base
│       ├── index.html          ← Accueil
│       ├── rendez_vous.html    ← Formulaire de réservation
│       ├── confirmation.html   ← Page de confirmation
│       ├── mes_rdv.html        ← Consulter / annuler ses RDV
│       ├── admin.html          ← Tableau de bord administrateur
│       └── login.html          ← Connexion admin
│
└── ansible/
    ├── deploy.yml              ← Playbook principal
    ├── inventory.ini           ← Serveurs cibles (IP Azure)
    ├── group_vars/all.yml      ← Variables globales
    └── roles/
        ├── database/           ← Installation MySQL + schéma
        ├── app/                ← Flask + Gunicorn + systemd
        └── nginx/              ← Proxy inverse Nginx
```

---

## ⚙️ Prérequis (sur votre machine locale)

```bash
# Installer Ansible
pip install ansible

# Vérifier
ansible --version
```

---

## 🚀 Déploiement en 3 étapes

### Étape 1 – Configurer l'inventaire

Ouvre `ansible/inventory.ini` :

```ini
[master]
4.204.25.28  ansible_user=admin12  ansible_ssh_private_key_file=~/.ssh/tay.pem
```
<img width="972" height="256" alt="image" src="https://github.com/user-attachments/assets/36db2d3d-bd07-41df-91c9-ef0cbcdcf8d5" />


### Étape 2 – Ajustez les mots de passe (optionnel)

Ouvrez `ansible/group_vars/all.yml` et modifiez si nécessaire :

```yaml
mysql_root_password: "VotreMotDePasseRoot!"
mysql_password:      "VotreMotDePasseApp!"
secret_key:          "une-clé-secrète-longue-et-aléatoire"
server_name:         "votre-ip-ou-domaine.com"
```

### Étape 3 – Lancer le déploiement

```bash
cd hopital-yaounde/ansible
ansible-playbook -i inventory.ini deploy.yml
```
<img width="1484" height="490" alt="image" src="https://github.com/user-attachments/assets/728af0ad-5ace-49b3-aeda-fbd7fbb0bcc3" />
<img width="1916" height="1030" alt="image" src="https://github.com/user-attachments/assets/f64f848a-8e94-4942-8781-e97d04a1cad0" />



Ansible va automatiquement :
1. Installer et configurer **MySQL** (base + tables + données)
2. Déployer l'application **Flask** avec **Gunicorn** (service systemd)
3. Configurer **Nginx** comme proxy inverse
4. Vérifier que l'application répond correctement
<img width="1923" height="645" alt="image" src="https://github.com/user-attachments/assets/862f5cb3-b458-421d-bad4-0b083b065ea5" />

---

## 🌐 Accès à l'application

| URL | Description |
|-----|-------------|
| `http://4.204.25.28/` | Page d'accueil patients |
| `http://4.204.25.28/rendez-vous` | Prendre un rendez-vous |
| `http://4.204.25.28/mes-rendez-vous` | Consulter / annuler ses RDV |
| `http://4.204.25.28/admin` | Tableau de bord (admin) |
| `(http://4.204.25.28/login` | Connexion administration |

**Identifiants administrateur :**
- Utilisateur : `admin`
- Mot de passe : `Admin2024!`

---

## 🔄 Mettre à jour l'application

Après modification du code, relancez simplement :

```bash
ansible-playbook -i inventory.ini deploy.yml
```

Pour ne redéployer que l'application (sans toucher à la base) :

```bash
ansible-playbook -i inventory.ini deploy.yml --tags app
```

---

## 🛠️ Commandes utiles sur le serveur

```bash
# Voir l'état des services
sudo systemctl status hopital-yaounde
sudo systemctl status nginx
sudo systemctl status mysql

# Redémarrer l'application
sudo systemctl restart hopital-yaounde

# Voir les logs en temps réel
sudo journalctl -u hopital-yaounde -f
sudo tail -f /var/log/nginx/hopital-error.log

# Accéder à la base de données
mysql -u hopital_user -p hopital_yaounde
```
<img width="1442" height="332" alt="image" src="https://github.com/user-attachments/assets/3671595a-9959-4a5f-8c1e-7a9f7a6b569c" />

---

## 🗄️ Base de données

| Table | Description |
|-------|-------------|
| `services` | Services médicaux (Cardiologie, Pédiatrie…) |
| `medecins` | Médecins par service |
| `rendez_vous` | Réservations des patients |

**8 services** et **12 médecins** sont pré-chargés automatiquement.

---

## 🔐 Sécurité en production

- Changer tous les mots de passe dans `group_vars/all.yml`
- Activer HTTPS avec Let's Encrypt (Certbot)
- Restreindre l'accès à `/admin` par IP si possible
- Utiliser Ansible Vault pour chiffrer les mots de passe :
  ```bash
  ansible-vault encrypt group_vars/all.yml
  ansible-playbook -i inventory.ini deploy.yml --ask-vault-pass
  ```
---- 
# 🌤️ verification base de donnee

-- Voir toutes les tables
```bash
SHOW TABLES;
```
-- Voir tous les rendez-vous
```bash
SELECT * FROM rendez_vous;
```
-- Voir les rendez-vous avec les détails (service + médecin)
```bash
SELECT 
    r.id,
    r.prenom,
    r.nom,
    r.telephone,
    s.nom AS service,
    CONCAT('Dr. ', m.nom, ' ', m.prenom) AS medecin,
    r.date_rdv,
    r.heure_rdv,
    r.statut
FROM rendez_vous r
JOIN services s ON r.service_id = s.id
JOIN medecins m ON r.medecin_id = m.id
ORDER BY r.date_rdv, r.heure_rdv;
```

-- Voir les rendez-vous du jour
```bash
SELECT * FROM rendez_vous WHERE date_rdv = CURDATE();
```

-- Voir tous les médecins
```bash
SELECT * FROM medecins;
```

-- Voir tous les services
```bash
SELECT * FROM services;
```

-- Compter les rendez-vous par statut
```bash
SELECT statut, COUNT(*) AS total FROM rendez_vous GROUP BY statut;
```

-- Quitter MySQL
```bash
EXIT;
```
-----
-- pour se connecter à la base de donnée:
```bash
sudo mysql -u root -p
```
# Mot de passe : taylor

-- Choisir la base
```bash
USE hopital_yaounde;
```

-- Voir toutes les bases disponibles
```bash
SHOW DATABASES;
```
<img width="980" height="664" alt="image" src="https://github.com/user-attachments/assets/11289dbd-c239-4d8e-9435-33c7eead8b08" />
