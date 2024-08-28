# API de Paiement Flexible

## Sommaire

1. Introduction
   - Aperçu du projet
   - Fonctionnalités principales

2. Installation
   - Prérequis
   - Configuration de l'environnement
   - Installation des dépendances
   - Utilisation de Docker

3. Configuration
   - Variables d'environnement
   - Configuration des fournisseurs de paiement

4. Structure du projet
   - Arborescence des fichiers
   - Description des principaux modules

5. Utilisation de l'API
   - Endpoints disponibles
   - Exemples de requêtes et réponses

6. Fournisseurs de paiement
   - Fournisseurs supportés
   - Ajout d'un nouveau fournisseur

7. Gestion des transactions
   - Création d'une transaction
   - Vérification du statut
   - Webhooks

8. Gestion des abonnements
   - Création d'un abonnement
   - Mise à jour et annulation

9. Base de données
   - Modèles de données
   - Migrations

10. Tests

11. FAQ


# 1. Introduction

## Aperçu du projet

L'API de Paiement Flexible est une solution robuste et modulaire conçue pour gérer les transactions de paiement et les abonnements avec différents fournisseurs de paiement. Cette API offre une interface unifiée pour intégrer facilement plusieurs passerelles de paiement, permettant aux développeurs de créer des applications de commerce électronique flexibles et évolutives.

## Fonctionnalités principales

- **Gestion multi-fournisseurs** : Intégration transparente avec plusieurs fournisseurs de paiement (actuellement Stripe et PayPal) via une interface unifiée.
- **Transactions de paiement** : Création, vérification et gestion des transactions de paiement uniques.
- **Gestion des abonnements** : Mise en place, mise à jour et annulation d'abonnements récurrents.
- **Webhooks** : Traitement des webhooks pour les mises à jour en temps réel des statuts de paiement et d'abonnement.
- **Base de données intégrée** : Stockage et gestion des transactions et des abonnements dans une base de données SQL.
- **API RESTful** : Endpoints bien définis pour toutes les opérations, suivant les principes REST.
- **Documentation automatique** : Interface Swagger/OpenAPI pour une documentation et des tests d'API faciles.
- **Extensibilité** : Architecture conçue pour faciliter l'ajout de nouveaux fournisseurs de paiement.

# 2. Installation

## Prérequis

Avant d'installer l'API de Paiement Flexible, assurez-vous d'avoir les éléments suivants installés sur votre système :

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Un environnement virtuel (recommandé)
- Git (pour cloner le dépôt)

## Configuration de l'environnement

1. Clonez le dépôt :
```
git clone https://github.com/votre-nom/api-paiement-flexible.git
cd api-paiement-flexible
```

2. Créez un environnement virtuel :
```
python -m venv venv
```

3. Activez l'environnement virtuel :
   - Sur Windows :
     ```
     venv\Scripts\activate
     ```
   - Sur macOS et Linux :
     ```
     source venv/bin/activate
     ```

4. Créez un fichier `.env` à la racine du projet et configurez les variables d'environnement nécessaires :
```
DATABASE_URL=sqlite:///./test.db
STRIPE_PUBLIC_KEY=votre_cle_publique_stripe
STRIPE_SECRET_KEY=votre_cle_secrete_stripe
PAYPAL_CLIENT_ID=votre_client_id_paypal
PAYPAL_CLIENT_SECRET=votre_client_secret_paypal
PAYPAL_MODE=sandbox
BASE_URL=http://localhost:8000
```

## Installation des dépendances

Installez les dépendances du projet en utilisant le fichier `requirements.txt` :

```
pip install -r requirements.txt
```

Pour référence, voici le contenu du fichier `requirements.txt` :


```1:9:requirements.txt
fastapi
uvicorn
sqlalchemy
pydantic
pydantic-settings
python-dotenv
stripe
requests
paypalrestsdk
```

## Utilisation de Docker

Pour faciliter le déploiement et la gestion de l'environnement, nous fournissons également une configuration Docker. Voici les étapes pour utiliser Docker avec notre API :

1. Assurez-vous d'avoir Docker installé sur votre système.

2. À la racine du projet, créez un fichier `Dockerfile` avec le contenu suivant :

```Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. Pour construire l'image Docker, exécutez la commande suivante à la racine du projet :

```
docker build -t api-paiement-flexible .
```

4. Pour démarrer un conteneur à partir de cette image, utilisez la commande :

```
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./test.db -e STRIPE_PUBLIC_KEY=votre_cle_publique_stripe -e STRIPE_SECRET_KEY=votre_cle_secrete_stripe -e PAYPAL_CLIENT_ID=votre_client_id_paypal -e PAYPAL_CLIENT_SECRET=votre_client_secret_paypal -e PAYPAL_MODE=sandbox -e BASE_URL=http://localhost:8000 api-paiement-flexible
```

Assurez-vous de remplacer les valeurs des variables d'environnement par vos propres clés et configurations.

5. L'API sera accessible à l'adresse `http://localhost:8000`.

Voici la rédaction pour la section Configuration du README :

# 3. Configuration

## Variables d'environnement

L'API de Paiement Flexible utilise des variables d'environnement pour gérer la configuration. Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```
DATABASE_URL=sqlite:///./test.db
STRIPE_PUBLIC_KEY=votre_cle_publique_stripe
STRIPE_SECRET_KEY=votre_cle_secrete_stripe
PAYPAL_CLIENT_ID=votre_client_id_paypal
PAYPAL_CLIENT_SECRET=votre_client_secret_paypal
PAYPAL_MODE=sandbox
BASE_URL=http://localhost:8000
```

Assurez-vous de remplacer les valeurs par vos propres clés d'API et configurations.

## Configuration des fournisseurs de paiement

### Stripe

1. Créez un compte Stripe sur https://stripe.com/
2. Obtenez vos clés API dans le tableau de bord Stripe
3. Configurez les webhooks Stripe pour pointer vers `{BASE_URL}/webhook/stripe`

### PayPal

1. Créez un compte développeur PayPal sur https://developer.paypal.com/
2. Créez une application pour obtenir vos identifiants Client ID et Secret
3. Configurez les webhooks PayPal pour pointer vers `{BASE_URL}/webhook/paypal`

Pour ajouter un nouveau fournisseur de paiement, suivez ces étapes :

1. Créez une nouvelle classe dans le dossier providers/ qui hérite de PaymentProvider
2. Implémentez les méthodes requises (create_payment, create_subscription, cancel_subscription, etc.)
Ajoutez les variables d'environnement nécessaires dans le fichier .env
4. Mettez à jour la fonction load_payment_providers() dans utils/provider_loader.py pour inclure le nouveau fournisseur
5. Ajoutez des tests pour le nouveau fournisseur dans un nouveau fichier de test (par exemple, test_new_provider.py)

L'étape 5 est importante car des tests spécifiques sont créés pour chaque fournisseur. Ces tests incluent la création de transactions, d'abonnements, l'annulation d'abonnements et la simulation de webhooks.

# 4. Structure du projet

## Arborescence des fichiers

```
.
├── Dockerfile
├── .env
├── README.md
├── config.py
├── database.py
├── main.py
├── models
│   ├── subscription.py
│   └── transaction.py
├── providers
│   ├── base.py
│   ├── paypal.py
│   └── stripe.py
├── requirements.txt
├── routes
│   ├── subscriptions.py
│   └── transactions.py
├── schemas
│   ├── subscription.py
│   └── transaction.py
├── test_paypal.py
├── test_stripe.py
└── utils
    └── provider_loader.py
```

## Description des principaux modules

1. **main.py** : Point d'entrée de l'application FastAPI. Il initialise l'application, charge les fournisseurs de paiement et inclut les routes.

2. **config.py** : Gère la configuration de l'application, y compris le chargement des variables d'environnement.

3. **database.py** : Configure la connexion à la base de données et fournit une session de base de données.

4. **models/** : Contient les modèles de données SQLAlchemy pour les transactions et les abonnements.
   - **transaction.py** : Définit le modèle de données pour les transactions.
   - **subscription.py** : Définit le modèle de données pour les abonnements.

5. **providers/** : Contient les classes pour chaque fournisseur de paiement.
   - **base.py** : Définit la classe de base `PaymentProvider` avec les méthodes abstraites.
   - **stripe.py** : Implémente le fournisseur de paiement Stripe.
   - **paypal.py** : Implémente le fournisseur de paiement PayPal.

6. **routes/** : Contient les définitions des routes de l'API.
   - **transactions.py** : Gère les routes liées aux transactions.
   - **subscriptions.py** : Gère les routes liées aux abonnements.

7. **schemas/** : Contient les schémas Pydantic pour la validation des données d'entrée et de sortie.
   - **transaction.py** : Définit les schémas pour les transactions.
   - **subscription.py** : Définit les schémas pour les abonnements.

8. **utils/** :
   - **provider_loader.py** : Contient la logique pour charger dynamiquement les fournisseurs de paiement.

9. **test_stripe.py** et **test_paypal.py** : Fichiers de test pour les fournisseurs Stripe et PayPal respectivement.

10. **Dockerfile** : Définit la configuration pour créer une image Docker de l'application.

11. **requirements.txt** : Liste toutes les dépendances Python nécessaires pour l'application.

Les fournisseurs de paiement sont isolés dans leurs propres modules, permettant d'ajouter facilement de nouveaux fournisseurs sans affecter le reste du code.

# 5. Utilisation de l'API

## Endpoints disponibles

L'API de Paiement Flexible offre les endpoints suivants :

1. **POST /transactions/** : Créer une nouvelle transaction
2. **GET /transactions/{transaction_id}** : Récupérer les détails d'une transaction
3. **POST /subscriptions/** : Créer un nouvel abonnement
4. **GET /subscriptions/{subscription_id}** : Récupérer les détails d'un abonnement
5. **PUT /subscriptions/{subscription_id}** : Mettre à jour un abonnement
6. **DELETE /subscriptions/{subscription_id}** : Annuler un abonnement
7. **POST /webhook/{provider}** : Endpoint pour les webhooks des fournisseurs de paiement

## Exemples de requêtes et réponses

### Créer une nouvelle transaction

**Requête :**

```
POST /transactions/?provider=stripe
Content-Type: application/json

{
  "amount": 100.0,
  "currency": "EUR",
  "payment_details": {"customer_email": "client@example.com"},
  "success_url": "https://example.com/success",
  "cancel_url": "https://example.com/cancel",
  "description": "Achat de produit XYZ",
  "custom_metadata": {"order_id": "ORD-12345"}
}
```

**Réponse :**

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "amount": 100.0,
  "currency": "EUR",
  "status": "pending",
  "provider": "StripeProvider",
  "provider_transaction_id": "pi_3NqKjHXXXXXXXXXX1234567890",
  "client_secret": "pi_3NqKjHXXXXXXXXXX1234567890_secret_XXXXXXXXXXXXXXXXXXXXXXXX",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "created_at": "2023-07-25T14:30:00Z",
  "metadata": {"order_id": "ORD-12345"},
  "description": "Achat de produit XYZ"
}
```

### Créer un nouvel abonnement

**Requête :**

```
POST /subscriptions/?provider=paypal
Content-Type: application/json

{
  "user_id": 1,
  "plan_id": "monthly_plan",
  "amount": 19.99,
  "currency": "EUR",
  "interval": "month",
  "interval_count": 1,
  "payment_details": {
    "success_url": "http://example.com/success",
    "cancel_url": "http://example.com/cancel"
  }
}
```

**Réponse :**

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "user_id": 1,
  "plan_id": "monthly_plan",
  "amount": 19.99,
  "currency": "EUR",
  "status": "active",
  "provider": "PayPalProvider",
  "provider_subscription_id": "I-BWXXXXXXXX",
  "created_at": "2023-07-25T15:00:00Z",
  "next_billing_date": "2023-08-25T15:00:00Z",
  "cancel_at_period_end": false
}
```

Pour plus de détails sur les paramètres acceptés et les réponses pour chaque endpoint, veuillez consulter la documentation Swagger/OpenAPI disponible à l'adresse `http://localhost:8000/docs` lorsque l'API est en cours d'exécution.

# 6. Fournisseurs de paiement

## Fournisseurs supportés

Actuellement, l'API de Paiement Flexible prend en charge deux fournisseurs de paiement :

1. **Stripe** : Un service de paiement en ligne complet, offrant des fonctionnalités pour les transactions uniques et les abonnements récurrents.

2. **PayPal** : Une plateforme de paiement en ligne largement utilisée, permettant les transactions et les abonnements.

Ces fournisseurs sont implémentés dans les fichiers suivants :

- providers/stripe.py
- providers/paypal.py

## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur de paiement à l'API, suivez ces étapes rigoureusement :

1. **Créer une nouvelle classe de fournisseur** :
   - Créez un nouveau fichier dans le dossier `providers/`, par exemple `new_provider.py`.
   - Définissez une classe qui hérite de `PaymentProvider` (définie dans `providers/base.py`).
   - Implémentez toutes les méthodes abstraites requises.

2. **Implémenter les méthodes requises** :
   - `create_payment`
   - `create_subscription`
   - `cancel_subscription`
   - `get_payment_status`
   - `get_subscription_status`
   - `handle_webhook`

3. **Ajouter les variables d'environnement** :
   - Ajoutez les variables d'environnement nécessaires pour le nouveau fournisseur dans le fichier `.env`.
   - Mettez à jour le fichier `config.py` pour inclure ces nouvelles variables.

4. **Mettre à jour le chargeur de fournisseurs** :
   - Modifiez le fichier `utils/provider_loader.py` pour inclure le nouveau fournisseur.

5. **Créer des tests** :
   - Ajoutez un nouveau fichier de test, par exemple `test_new_provider.py`.
   - Implémentez des tests pour toutes les fonctionnalités du nouveau fournisseur.

6. **Mettre à jour la documentation** :
   - Ajoutez des informations sur le nouveau fournisseur dans le README.md.
   - Mettez à jour la documentation API si nécessaire.

# 7. Gestion des transactions

## Création d'une transaction

Le processus de création d'une transaction suit les étapes suivantes :

1. L'utilisateur envoie une requête POST à l'endpoint `/transactions/` avec les détails de la transaction.
2. L'API vérifie et valide les données d'entrée.
3. Le fournisseur de paiement approprié est sélectionné en fonction du paramètre `provider`.
4. L'API appelle la méthode `create_payment` du fournisseur sélectionné.
5. Le fournisseur de paiement traite la demande et renvoie les détails de la transaction.
6. L'API enregistre la transaction dans la base de données.
7. Une réponse est renvoyée à l'utilisateur avec les détails de la transaction, y compris l'URL de paiement.

## Vérification du statut

La vérification du statut d'une transaction peut se faire de deux manières :

1. **Vérification active** : L'utilisateur peut envoyer une requête GET à l'endpoint `/transactions/{transaction_id}` pour obtenir le statut actuel de la transaction.

2. **Mise à jour passive** : Le statut est automatiquement mis à jour lorsque l'API reçoit un webhook du fournisseur de paiement.

## Webhooks

Les webhooks jouent un rôle crucial dans la mise à jour en temps réel du statut des transactions :

1. Chaque fournisseur de paiement est configuré pour envoyer des webhooks à l'endpoint `/webhook/{provider}`.
2. Lorsqu'un webhook est reçu, l'API l'authentifie et le valide.
3. Le webhook est traité par la méthode `webhook` du fournisseur approprié.
4. En fonction des informations du webhook, l'API met à jour le statut de la transaction dans la base de données.
5. Si nécessaire, des actions supplémentaires sont déclenchées (par exemple, envoi d'un e-mail de confirmation).

Cette approche permet une gestion en temps réel des transactions, assurant que l'état des paiements dans votre système est toujours à jour.

# 8. Gestion des abonnements

## Création d'un abonnement

Le processus de création d'un abonnement suit les étapes suivantes :

1. L'utilisateur envoie une requête POST à l'endpoint `/subscriptions/` avec les détails de l'abonnement.
2. L'API vérifie et valide les données d'entrée.
3. Le fournisseur de paiement approprié est sélectionné en fonction du paramètre `provider`.
4. L'API appelle la méthode `create_subscription` du fournisseur sélectionné.
5. Le fournisseur de paiement traite la demande et renvoie les détails de l'abonnement.
6. L'API enregistre l'abonnement dans la base de données.
7. Une réponse est renvoyée à l'utilisateur avec les détails de l'abonnement, y compris l'ID de l'abonnement chez le fournisseur.

## Mise à jour et annulation

La mise à jour et l'annulation des abonnements sont gérées de manière similaire :

1. Mise à jour d'un abonnement :
   - L'utilisateur envoie une requête PUT à l'endpoint `/subscriptions/{subscription_id}` avec les nouvelles informations.
   - L'API vérifie les modifications et appelle la méthode appropriée du fournisseur de paiement.
   - Les changements sont reflétés dans la base de données locale.

2. Annulation d'un abonnement :
   - L'utilisateur envoie une requête DELETE à l'endpoint `/subscriptions/{subscription_id}`.
   - L'API appelle la méthode `cancel_subscription` du fournisseur de paiement.
   - Le statut de l'abonnement est mis à jour dans la base de données locale.

Dans les deux cas, les webhooks jouent un rôle crucial :

- Les fournisseurs de paiement envoient des webhooks pour notifier des changements d'état des abonnements.
- L'API traite ces webhooks et met à jour la base de données en conséquence.
- Cela garantit que l'état des abonnements dans votre système reste synchronisé avec celui du fournisseur de paiement.

# 9. Base de données

## Modèles de données

L'API de Paiement Flexible utilise SQLAlchemy comme ORM (Object-Relational Mapping) pour gérer les interactions avec la base de données. Les principaux modèles de données sont définis dans le dossier `models/`.

### Transaction

Le modèle `Transaction` représente une transaction de paiement unique. Il est défini dans `models/transaction.py` et comprend les champs suivants :

- `id` : Identifiant unique de la transaction
- `amount` : Montant de la transaction
- `currency` : Devise de la transaction
- `status` : Statut actuel de la transaction (ex: pending, completed, failed)
- `provider` : Fournisseur de paiement utilisé
- `provider_transaction_id` : Identifiant de la transaction chez le fournisseur
- `success_url` : URL de redirection en cas de succès
- `cancel_url` : URL de redirection en cas d'annulation
- `created_at` : Date et heure de création de la transaction
- `checkout_url` : URL de paiement fournie par le fournisseur
- `metadata` : Métadonnées personnalisées associées à la transaction
- `description` : Description de la transaction

### Subscription

Le modèle `Subscription` représente un abonnement récurrent. Il est défini dans `models/subscription.py` et comprend les champs suivants :

- `id` : Identifiant unique de l'abonnement
- `user_id` : Identifiant de l'utilisateur associé à l'abonnement
- `plan_id` : Identifiant du plan d'abonnement
- `amount` : Montant de l'abonnement
- `currency` : Devise de l'abonnement
- `status` : Statut actuel de l'abonnement (ex: active, cancelled, expired)
- `provider` : Fournisseur de paiement utilisé
- `provider_subscription_id` : Identifiant de l'abonnement chez le fournisseur
- `created_at` : Date et heure de création de l'abonnement
- `next_billing_date` : Date du prochain prélèvement
- `cancel_at_period_end` : Indique si l'abonnement sera annulé à la fin de la période en cours

## Migrations

L'API utilise Alembic pour gérer les migrations de base de données. Cela permet de versionner le schéma de la base de données et de faciliter les mises à jour.

Pour créer une nouvelle migration :

1. Modifiez les modèles de données dans le dossier `models/`.
2. Exécutez la commande suivante pour générer un script de migration :

```
alembic revision --autogenerate -m "Description de la migration"
```

3. Vérifiez le script de migration généré dans le dossier `alembic/versions/`.
4. Appliquez la migration avec la commande :

```
alembic upgrade head
```

Pour revenir à une version précédente de la base de données, utilisez :

```
alembic downgrade <revision>
```

Où `<revision>` est l'identifiant de la révision souhaitée.

Pour plus de détails sur la configuration de la base de données, vous pouvez consulter le fichier `database.py` à la racine du projet.

# 10. Tests

Les tests pour l'API de Paiement Flexible sont implémentés dans deux fichiers principaux : `test_stripe.py` et `test_paypal.py`. Ces tests vérifient le bon fonctionnement des intégrations avec Stripe et PayPal respectivement.

## Fonctionnalités testées

Les tests couvrent les fonctionnalités suivantes pour chaque fournisseur :

1. Création de transaction
2. Création d'abonnement
3. Annulation d'abonnement
4. Simulation de webhooks pour les transactions et les abonnements

## Procédure d'utilisation des tests

Pour exécuter les tests, suivez ces étapes :

1. Assurez-vous que l'API est en cours d'exécution localement.

2. Ouvrez un terminal et naviguez jusqu'au répertoire du projet.

3. Pour exécuter les tests Stripe :
   ```
   python test_stripe.py
   ```

4. Pour exécuter les tests PayPal :
   ```
   python test_paypal.py
   ```

Chaque fichier de test exécutera une série de tests qui créeront des transactions et des abonnements, simuleront des webhooks, et vérifieront les réponses de l'API.

Les résultats des tests seront affichés dans la console, montrant les codes de statut HTTP et les réponses de l'API pour chaque opération.

# 11. FAQ

**Q1 : Comment puis-je ajouter un nouveau fournisseur de paiement ?**
R : Pour ajouter un nouveau fournisseur, suivez les étapes décrites dans la section "Ajout d'un nouveau fournisseur" du README :


```400:430:README.md
## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur de paiement à l'API, suivez ces étapes rigoureusement :

1. **Créer une nouvelle classe de fournisseur** :
   - Créez un nouveau fichier dans le dossier `providers/`, par exemple `new_provider.py`.
   - Définissez une classe qui hérite de `PaymentProvider` (définie dans `providers/base.py`).
   - Implémentez toutes les méthodes abstraites requises.

2. **Implémenter les méthodes requises** :
   - `create_payment`
   - `create_subscription`
   - `cancel_subscription`
   - `get_payment_status`
   - `get_subscription_status`
   - `handle_webhook`

3. **Ajouter les variables d'environnement** :
   - Ajoutez les variables d'environnement nécessaires pour le nouveau fournisseur dans le fichier `.env`.
   - Mettez à jour le fichier `config.py` pour inclure ces nouvelles variables.

4. **Mettre à jour le chargeur de fournisseurs** :
   - Modifiez le fichier `utils/provider_loader.py` pour inclure le nouveau fournisseur.

5. **Créer des tests** :
   - Ajoutez un nouveau fichier de test, par exemple `test_new_provider.py`.
   - Implémentez des tests pour toutes les fonctionnalités du nouveau fournisseur.

6. **Mettre à jour la documentation** :
   - Ajoutez des informations sur le nouveau fournisseur dans le README.md.
   - Mettez à jour la documentation API si nécessaire.
```


**Q2 : Comment fonctionnent les webhooks dans cette API ?**
R : Les webhooks sont utilisés pour mettre à jour en temps réel le statut des transactions et des abonnements. Chaque fournisseur envoie des webhooks à l'endpoint `/webhook/{provider}`. L'API traite ces webhooks et met à jour la base de données en conséquence.

**Q3 : Quels sont les principaux endpoints de l'API ?**
R : Les principaux endpoints sont listés dans la section "Endpoints disponibles" du README :


```288:296:README.md
L'API de Paiement Flexible offre les endpoints suivants :

1. **POST /transactions/** : Créer une nouvelle transaction
2. **GET /transactions/{transaction_id}** : Récupérer les détails d'une transaction
3. **POST /subscriptions/** : Créer un nouvel abonnement
4. **GET /subscriptions/{subscription_id}** : Récupérer les détails d'un abonnement
5. **PUT /subscriptions/{subscription_id}** : Mettre à jour un abonnement
6. **DELETE /subscriptions/{subscription_id}** : Annuler un abonnement
7. **POST /webhook/{provider}** : Endpoint pour les webhooks des fournisseurs de paiement
```


**Q4 : Comment puis-je exécuter les tests ?**
R : Pour exécuter les tests, assurez-vous que l'API est en cours d'exécution localement, puis exécutez `python test_stripe.py` pour les tests Stripe et `python test_paypal.py` pour les tests PayPal.

**Q5 : Comment gérer les migrations de base de données ?**
R : L'API utilise Alembic pour les migrations. Pour créer une nouvelle migration, modifiez les modèles dans `models/`, puis exécutez `alembic revision --autogenerate -m "Description"`. Appliquez la migration avec `alembic upgrade head`.

**Q6 : Quelles sont les variables d'environnement nécessaires ?**
R : Les principales variables d'environnement incluent les clés API pour Stripe et PayPal, ainsi que les configurations de base de données. Consultez le fichier `.env.example` pour la liste complète.

**Q7 : Comment puis-je déployer l'API en production ?**
R : L'API peut être déployée en utilisant Docker. Utilisez le Dockerfile fourni pour créer une image, puis déployez-la sur votre plateforme préférée (AWS, Google Cloud, etc.). Assurez-vous de configurer correctement les variables d'environnement en production.

**Q8 : L'API prend-elle en charge les paiements récurrents ?**
R : Oui, l'API supporte les abonnements récurrents via les endpoints `/subscriptions/`. Vous pouvez créer, mettre à jour et annuler des abonnements.

**Q9 : Comment puis-je gérer les erreurs de paiement ?**
R : Les erreurs de paiement sont gérées au niveau du fournisseur et communiquées via les webhooks. Assurez-vous de bien configurer la gestion des erreurs dans votre implémentation et de vérifier les logs pour les détails des erreurs.

**Q10 : L'API est-elle conforme aux normes de sécurité des paiements ?**
R : L'API est conçue pour être conforme aux normes de sécurité, mais la conformité finale dépend de votre implémentation spécifique et de votre environnement de déploiement. Assurez-vous de suivre les meilleures pratiques de sécurité et de vous conformer aux réglementations locales en matière de paiement.