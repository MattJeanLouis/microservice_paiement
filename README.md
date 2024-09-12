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
   

# 1. Introduction

## Aperçu du projet

L'API de Paiement Flexible est une solution robuste et modulaire conçue pour gérer les transactions de paiement et les abonnements avec différents fournisseurs de paiement. Cette API offre une interface unifiée pour intégrer facilement plusieurs passerelles de paiement, permettant aux développeurs de créer des applications de commerce électronique flexibles et évolutives.

## Fonctionnalités principales

- **Gestion multi-fournisseurs** : Intégration transparente avec plusieurs fournisseurs de paiement (actuellement Stripe, PayPal et Revolut) via une interface unifiée.
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
REVOLUT_PUBLIC_KEY=votre_cle_publique_revolut
REVOLUT_SECRET_KEY=votre_cle_secrete_revolut
REVOLUT_MODE=sandbox
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
pytest
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
docker run -p 8000:8000 --env-file .env api-paiement-flexible
```

Assurez-vous de remplacer les valeurs des variables d'environnement par vos propres clés et configurations.

5. L'API sera accessible à l'adresse `http://localhost:8000`.

Voici la rédaction pour la section Configuration du README :

# 3. Configuration

## Configuration des fournisseurs de paiement

### Stripe

1. Créez un compte Stripe sur https://stripe.com/
2. Obtenez vos clés API dans le tableau de bord Stripe
3. Configurez les webhooks Stripe pour pointer vers `{BASE_URL}/webhook/stripe`

### PayPal

1. Créez un compte développeur PayPal sur https://developer.paypal.com/
2. Créez une application pour obtenir vos identifiants Client ID et Secret
3. Configurez les webhooks PayPal pour pointer vers `{BASE_URL}/webhook/paypal`

### Revolut

1. Créez un compte développeur Revolut sur https://developer.revolut.com/
2. Créez une application pour obtenir vos clés API publique et secrète
3. Configurez les webhooks Revolut pour pointer vers `{BASE_URL}/webhook/revolut`

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
├── .gitignore
├── README.md
├── main.py
├── config.py
├── database.py
├── requirements.txt
├── models/
│   ├── customer.py
│   ├── subscription.py
│   └── transaction.py
├── providers/
│   ├── base.py
│   ├── paypal.py
│   ├── revolut.py
│   └── stripe.py
├── routes/
│   ├── customers.py
│   ├── products.py
│   ├── subscriptions.py
│   └── transactions.py
├── schemas/
│   ├── customer.py
│   ├── subscription.py
│   └── transaction.py
├── utils/
│   └── provider_loader.py
└── test_paypal.py
└── test_revolut.py
└── test_stripe.py
```

## Description des principaux modules

1. **main.py** : Point d'entrée de l'application FastAPI. Il initialise l'application, configure les routes pour les transactions, abonnements, clients et produits, et charge les fournisseurs de paiement.

2. **config.py** : Gère la configuration de l'application, y compris le chargement des variables d'environnement et la configuration des fournisseurs de paiement.

3. **database.py** : Configure la connexion à la base de données et fournit une session de base de données.

4. **models/** : Contient les modèles de données SQLAlchemy pour les transactions, abonnements et clients.
   - **customer.py** : Définit le modèle de données pour les clients.
   - **subscription.py** : Définit le modèle de données pour les abonnements.
   - **transaction.py** : Définit le modèle de données pour les transactions.

5. **providers/** : Contient les classes pour chaque fournisseur de paiement.
   - **base.py** : Définit la classe de base `PaymentProvider` avec les méthodes abstraites.
   - **stripe.py** : Implémente le fournisseur de paiement Stripe.
   - **paypal.py** : Implémente le fournisseur de paiement PayPal.
   - **revolut.py** : Implémente le fournisseur de paiement Revolut.

6. **routes/** : Contient les définitions des routes de l'API.
   - **customers.py** : Gère les routes liées aux clients.
   - **products.py** : Gère les routes liées aux produits.
   - **subscriptions.py** : Gère les routes liées aux abonnements.
   - **transactions.py** : Gère les routes liées aux transactions.

7. **schemas/** : Contient les schémas Pydantic pour la validation des données d'entrée et de sortie.
   - **customer.py** : Définit les schémas pour les clients.
   - **subscription.py** : Définit les schémas pour les abonnements.
   - **transaction.py** : Définit les schémas pour les transactions.

8. **utils/** :
   - **provider_loader.py** : Contient la logique pour charger dynamiquement les fournisseurs de paiement.

9. **test_paypal.py** et **test_stripe.py** : Fichiers de test pour les fournisseurs PayPal et Stripe respectivement.

10. **Dockerfile** : Définit la configuration pour créer une image Docker de l'application.

11. **requirements.txt** : Liste toutes les dépendances Python nécessaires pour l'application.

12. **.gitignore** : Spécifie les fichiers et dossiers intentionnellement non suivis à ignorer par Git.

Cette structure suit une architecture modulaire, séparant clairement les différentes préoccupations de l'application. Les fournisseurs de paiement sont isolés dans leurs propres modules, permettant d'ajouter facilement de nouveaux fournisseurs sans affecter le reste du code. Les routes sont organisées par domaine (transactions, abonnements, clients, produits), facilitant la maintenance et l'extension de l'API.

L'application utilise FastAPI comme framework web, SQLAlchemy pour l'ORM, et Pydantic pour la validation des données. Les tests sont organisés par fournisseur de paiement, permettant de vérifier spécifiquement les fonctionnalités de chaque intégration.

# 5. Utilisation de l'API

## Endpoints disponibles

L'API de Paiement offre les endpoints suivants :

1. **POST /transactions/** : Créer une nouvelle transaction
2. **GET /transactions/{transaction_id}** : Récupérer les détails d'une transaction
3. **GET /transactions/{transaction_id}/pay** : Obtenir l'URL de paiement pour une transaction
4. **GET /transactions/{transaction_id}/status** : Obtenir le statut d'une transaction
5. **POST /subscriptions/** : Créer un nouvel abonnement
6. **GET /subscriptions/{subscription_id}** : Récupérer les détails d'un abonnement
7. **PUT /subscriptions/{subscription_id}** : Mettre à jour un abonnement
8. **DELETE /subscriptions/{subscription_id}** : Annuler un abonnement
9. **POST /customers/** : Créer un nouveau client
10. **GET /customers/{customer_id}/payment-method** : Vérifier si un client a une méthode de paiement
11. **POST /products/** : Créer un nouveau produit et son prix (pour les abonnements)
12. **POST /webhook/{provider}** : Endpoint pour les webhooks des fournisseurs de paiement

Pour plus de détails sur les paramètres acceptés et les réponses pour chaque endpoint, veuillez consulter la documentation Swagger/OpenAPI disponible à l'adresse `http://localhost:8000/docs` lorsque l'API est en cours d'exécution.

# 6. Fournisseurs de paiement

## Fournisseurs supportés

Actuellement, l'API de Paiement Flexible prend en charge trois fournisseurs de paiement :

1. **Stripe** : Un service de paiement en ligne complet, offrant des fonctionnalités pour les transactions uniques et les abonnements récurrents.

2. **PayPal** : Une plateforme de paiement en ligne largement utilisée, permettant les transactions et les abonnements.

3. **Revolut** : Une solution de paiement moderne offrant des services bancaires et de paiement, adaptée aux transactions internationales.

Ces fournisseurs sont implémentés dans les fichiers suivants :

- providers/stripe.py
- providers/paypal.py
- providers/revolut.py

## Ajout d'un nouveau fournisseur

Pour ajouter un nouveau fournisseur de paiement à l'API, suivez ces étapes en vous basant sur l'implémentation de Stripe :

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
   - `create_customer`
   - `create_product`
   - `create_price`
   - `update_subscription`

3. **Ajouter les variables d'environnement** :
   - Ajoutez les variables d'environnement nécessaires pour le nouveau fournisseur dans le fichier `.env`.
   - Mettez à jour le fichier `config.py` pour inclure ces nouvelles variables.

4. **Mettre à jour le chargeur de fournisseurs** :
   - Modifiez le fichier `utils/provider_loader.py` pour inclure le nouveau fournisseur.

5. **Créer des tests** :
   - Ajoutez un nouveau fichier de test, par exemple `test_new_provider.py`.
   - Implémentez des tests pour toutes les fonctionnalités du nouveau fournisseur, en vous basant sur la structure de `test_stripe.py`.

Pour plus de détails sur l'implémentation, référez-vous au fichier `providers/stripe.py` :

# 7. Gestion des transactions

## Création d'une transaction

Le processus de création d'une transaction suit les étapes suivantes :

1. L'utilisateur envoie une requête POST à l'endpoint `/transactions/` avec les détails de la transaction.
2. L'API vérifie et valide les données d'entrée à l'aide du schéma Pydantic `TransactionCreate`.
3. Le fournisseur de paiement est sélectionné en fonction du paramètre `provider` passé dans la requête.
4. L'API crée d'abord une entrée de transaction dans la base de données avec un statut initial "pending".
5. L'API appelle ensuite la méthode `create_payment` du fournisseur sélectionné, en passant les détails de la transaction.
6. Le fournisseur de paiement traite la demande et renvoie les détails de la transaction, y compris l'URL de paiement.
7. L'API met à jour l'entrée de la transaction dans la base de données avec les informations renvoyées par le fournisseur, notamment l'ID de transaction du fournisseur et l'URL de paiement.
8. Une réponse est renvoyée à l'utilisateur avec les détails de la transaction, y compris l'ID de la transaction et l'URL de paiement.

Pour plus de détails sur l'implémentation, vous pouvez consulter le code source de routes/transactions.py

## Vérification du statut

La vérification du statut d'une transaction peut se faire de deux manières :

1. **Vérification active** : L'utilisateur peut envoyer une requête GET à l'endpoint `/transactions/{transaction_id}/status` pour obtenir le statut actuel de la transaction.

2. **Mise à jour passive** : Le statut est automatiquement mis à jour lorsque l'API reçoit un webhook du fournisseur de paiement.

La vérification active permet d'obtenir le statut le plus récent d'une transaction à tout moment. Elle est particulièrement utile pour les interfaces utilisateur qui nécessitent des mises à jour en temps réel ou pour vérifier l'état d'une transaction après que l'utilisateur a été redirigé vers l'URL de paiement.

Lorsqu'une requête de vérification de statut est effectuée, l'API interroge le fournisseur de paiement pour obtenir le statut le plus récent, puis met à jour la base de données locale si nécessaire. Cela garantit que le statut affiché est toujours à jour, même si un webhook n'a pas encore été reçu ou traité.

## Webhooks

Les webhooks jouent un rôle crucial dans la mise à jour en temps réel du statut des transactions et des abonnements :

1. Chaque fournisseur de paiement est configuré pour envoyer des webhooks à l'endpoint `/webhook/{provider}`.

2. Lorsqu'un webhook est reçu, l'API le traite via la méthode `process_webhook` du fournisseur approprié.

3. La méthode `process_webhook` analyse le type d'événement et extrait les informations pertinentes :
   - Pour les transactions, elle renvoie l'ID de la transaction et son statut.
   - Pour les abonnements, elle renvoie l'ID de l'abonnement et son statut.

4. En fonction des informations du webhook, l'API met à jour le statut de la transaction ou de l'abonnement dans la base de données.

5. Si nécessaire, des actions supplémentaires peuvent être déclenchées en fonction du type d'événement reçu.

Cette approche permet une gestion en temps réel des transactions et des abonnements, assurant que l'état des paiements dans votre système est toujours à jour.

# 8. Gestion des abonnements

## Création d'un abonnement

Le processus de création d'un abonnement suit les étapes suivantes :

1. L'utilisateur envoie une requête POST à l'endpoint `/subscriptions/` avec les détails de l'abonnement.
2. L'API vérifie et valide les données d'entrée à l'aide du schéma Pydantic `SubscriptionCreate`.
3. Le fournisseur de paiement est sélectionné en fonction du paramètre `provider` passé dans la requête.
4. L'API appelle la méthode `create_subscription` du fournisseur sélectionné, en passant les détails de l'abonnement.
5. Le fournisseur de paiement traite la demande et renvoie les détails de l'abonnement.
6. L'API crée une nouvelle entrée d'abonnement dans la base de données avec les informations renvoyées par le fournisseur.
7. Une réponse est renvoyée à l'utilisateur avec les détails de l'abonnement, y compris l'ID de l'abonnement local et l'ID de l'abonnement chez le fournisseur.

## Mise à jour et annulation

La mise à jour et l'annulation des abonnements sont gérées de manière similaire :

1. Mise à jour d'un abonnement :
   - L'utilisateur envoie une requête PUT à l'endpoint `/subscriptions/{subscription_id}` avec les nouvelles informations.
   - L'API vérifie les modifications et appelle la méthode `update_subscription` du fournisseur de paiement.
   - Les changements sont reflétés dans la base de données locale.

2. Annulation d'un abonnement :
   - L'utilisateur envoie une requête DELETE à l'endpoint `/subscriptions/{subscription_id}`.
   - L'API appelle la méthode `cancel_subscription` du fournisseur de paiement.
   - Le statut de l'abonnement est mis à jour dans la base de données locale.

Les webhooks jouent un rôle crucial dans la gestion des abonnements :

- Les fournisseurs de paiement envoient des webhooks pour notifier des changements d'état des abonnements.
- L'API traite ces webhooks via la méthode `process_webhook` du fournisseur de paiement.
- Les informations extraites du webhook sont utilisées pour mettre à jour la base de données, garantissant ainsi que l'état des abonnements dans votre système reste synchronisé avec celui du fournisseur de paiement.

# 9. Base de données

## Modèles de données

L'API de Paiement Flexible utilise SQLAlchemy comme ORM (Object-Relational Mapping) pour gérer les interactions avec la base de données. Les principaux modèles de données sont définis dans le dossier `models/`.

### Transaction

Le modèle `Transaction` représente une transaction de paiement unique. Il est défini dans `models/transaction.py` et comprend les champs suivants :

- `id` : Identifiant unique de la transaction
- `user_id` : Identifiant de l'utilisateur associé à la transaction
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
- `payment_details` : Détails supplémentaires du paiement (stockés en JSON)

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
- `metadata` : Métadonnées personnalisées associées à l'abonnement (stockées en JSON)
- `description` : Description de l'abonnement