# Deployment Steps

This is a catalog of the deployment steps needed to run Dabblebase on Carolina CloudApps.

## Part 1: Log into OC Terminal

To log into the `OC` terminal interface, access the terminal in the devcontainer.

Look in the top right in the CloudApps console and click on the username, click the drop down, and select “Copy Login Command”. From here select “Display Token”. Here, look for the line “Log in with this token” and copy the complete command beginning with oc login to your clipboard.

```
oc login <token here>
```

## Part 2: Create Databases and Redis Cluster

1. Create the admin database cluster by instantiating the PostgreSQL template by RedHat OpenShift with the settings:

   - Database Service Name: `db-admin-cluster`
   - PostgreSQL Database Name: `dabblebase_admin`
   - Version of PostgreSQL Image: `latest`
   - PostgreSQL Connection Username: `postgres`

   Once the admin database cluster is created, edit the YAML of the `db-admin-cluster` service so that the `port` property is set to `5433`. Keep `targetPort` the same.

   _This allows the service to connect to the database at port `5432` but expose the database endpoint at the port `5433` so that more than one database cluster is accessible._

2. Create the content database cluster by instantiating the PostgreSQL template by RedHat OpenShift with the settings:

   - Database Service Name: `db-content-cluster`
   - PostgreSQL Database Name: `postgres`
   - Version of PostgreSQL Image: `latest`
   - PostgreSQL Connection Username: `postgres`

   Once the admin database cluster is created, edit the YAML of the `db-content-cluster` service so that the `port` property is set to `5434`. Keep `targetPort` the same.

3. Create the redis cluster by instantiating the Redis template by RedHat OpenShift with the settings:

   - Database Service Name: `redis-cluster`
   - Version of Redis Image: `latest`

## Part 3: Create Secrets

1. Create a generic secret called `dabblebase-server-environment` using this command:

   ```
   oc create secret generic dabblebase-server-environment \
      --from-literal=MODE=production \
      --from-literal=HOST=<BASED ON HOST> \
      --from-literal=ADMIN_DB_USER=postgres \
      --from-literal=ADMIN_DB_PASSWORD=<FROM ADMIN DB SECRET> \
      --from-literal=ADMIN_DB_HOST=db-admin-cluster \
      --from-literal=ADMIN_DB_PORT=5433 \
      --from-literal=ADMIN_DB_DATABASE=dabblebase_admin \
      --from-literal=CONTENT_DB_USER=postgres \
      --from-literal=CONTENT_DB_PASSWORD=<FROM CONTENT DB SECRET> \
      --from-literal=CONTENT_DB_HOST=db-content-cluster \
      --from-literal=CONTENT_DB_PORT=5434 \
      --from-literal=CONTENT_DB_DATABASE=postgres \
      --from-literal=REDIS_HOST=redis-cluster \
      --from-literal=REDIS_PORT=6379 \
      --from-literal=REDIS_PASSWORD=<FROM REDIS SECRET> \
      --from-literal=PGBOUNCER_PASSWORD=<GENERATE SECRET> \
      --from-literal=JWT_SECRET=<GENERATE SECRET> \
      --from-literal=AUTH_MASTER_SECRET=<GENERATE SECRET> \
   ```

   **_NOTE: Add additional secrets to this command if needed and these steps are out of date._**

   Add key-value pairs for every environment variable in `/server/.env`. Use the information for the databases by finding the generated secrets for the database in OpenShift. Make sure that the port for the database is `5433` and `5434` respectively. For all passwords, generate the password in the DevContainer terminal using the command:

   ```
   openssl rand -hex 32
   ```

2. Create a generic secret called `dabblebase-realtime-environment` using this command:

   ```
   oc create secret generic dabblebase-realtime-environment \
      --from-literal=MODE=production \
      --from-literal=HOST=<BASED ON HOST> \
      --from-literal=ADMIN_DB_USER=postgres \
      --from-literal=ADMIN_DB_PASSWORD=<FROM ADMIN DB SECRET> \
      --from-literal=ADMIN_DB_HOST=db-admin-cluster \
      --from-literal=ADMIN_DB_PORT=5433 \
      --from-literal=ADMIN_DB_DATABASE=dabblebase_admin \
      --from-literal=CONTENT_DB_USER=postgres \
      --from-literal=CONTENT_DB_PASSWORD=<FROM CONTENT DB SECRET> \
      --from-literal=CONTENT_DB_HOST=db-content-cluster \
      --from-literal=CONTENT_DB_PORT=5434 \
      --from-literal=CONTENT_DB_DATABASE=postgres \
      --from-literal=AUTH_MASTER_SECRET=<GENERATE SECRET> \
   ```

   **_NOTE: Add additional secrets to this command if needed and these steps are out of date._**

   Add key-value pairs for every environment variable in `/server/.env`. Use the information for the databases by finding the generated secrets for the database in OpenShift and the passwords generated in step 1.

## Part 4: Create DeployKey to Link GitHub Repo to OpenShift

1. Create a private / public key pair using the following terminal command:

```
ssh-keygen -t ed25519 -C "GitHub Deploy Key" -f ./deploy_key
```

2. Go to the GitHub repository. Create a new deploy key in settings called `"CloudApps Deploy Key"` and paste in the contents of the generated `deploy_key.pub` file as the key's value.

3. Now, set the private deploy key as a secret in CloudApps:

   ```
   oc create secret generic dabblebase-deploykey \
       --from-file=ssh-privatekey=./deploy_key \
       --type=kubernetes.io/ssh-auth
   ```

4. Finally, link the secret to the “builder” process of OpenShift. This will allow OpenShift to use the secret when it pulls code from GitHub and builds the project.

   ```
   oc secrets link builder dabblebase-deploykey
   ```

## Part 5: Create the Applications

### Create the `web` Next.js Application

1. First, we will import the images required for the different containers to run.

   The first image to add is `node:22-alpine`, which is not included by CloudApps:

   ```
   oc import-image node-22-alpine --from=docker.io/library/node:22-alpine --confirm
   ```

2. Then, we will create the web app, which consists of running three commands:

   First, we need to create the base app.

   ```
   oc new-app node-22-alpine~git@github.com:dabblebase/dabblebase.git#main \
   --source-secret=dabblebase-deploykey \
   --name=web \
   --strategy=docker
   ```

   Note that this should create an app called `web`, but this should fail - we need to specify the location of the `Dockerfile`, which we do below:

   ```
   oc patch buildconfig web --type=merge -p '{
       "spec": {
       "source": {
           "contextDir": "."
       },
       "strategy": {
           "dockerStrategy": {
               "dockerfilePath": "deploy/Dockerfile.web"
           }
       }
   }
   }'
   ```

   Finally, we rebuild the application.

   ```
   oc start-build web
   ```

3. Now, create the service that exposes the application.

   ```
   oc expose deployment web \
   --port=80 \
   --target-port=8002
   ```

4. Finally, expose the route.

   ```
   oc create route edge dabblebase-web \
   --service=web \
   --hostname=www.dabblebase.dev
   ```

### Create the `api` FastAPI Application

1. First, we need to create the base app.

   ```
   oc new-app python:3.12~git@github.com:dabblebase/dabblebase.git#main \
   --source-secret=dabblebase-deploykey \
   --name=api \
   --strategy=docker
   ```

2. Then, specify the location of the API Dockerfile:

   ```
   oc patch buildconfig api --type=merge -p '{
       "spec": {
       "source": {
           "contextDir": "."
       },
       "strategy": {
           "dockerStrategy": {
               "dockerfilePath": "deploy/Dockerfile.api"
           }
       }
   }
   }'
   ```

   Then, set the secrets to the server secrets:

   ```
   oc set env deployment/api --from=secret/dabblebase-server-environment
   ```

   Finally, we rebuild the application.

   ```
   oc start-build api
   ```

3. Now, create the service that exposes the application.

   ```
   oc expose deployment api \
   --port=80 \
   --target-port=8001
   ```

4. Then, we need to create routes that should redirect to the API, which are `/api`, `/docs`, `/auth`, and `openapi.json`

   ```
   oc create route edge dabblebase-api \
   --service=api \
   --hostname=www.dabblebase.dev \
   --path=/api
   ```

   ```
   oc create route edge dabblebase-docs \
   --service=api \
   --hostname=www.dabblebase.dev \
   --path=/docs
   ```

   ```
   oc create route edge dabblebase-auth \
   --service=api \
   --hostname=www.dabblebase.dev \
   --path=/auth
   ```

   ```
   oc create route edge dabblebase-openapi \
   --service=api \
   --hostname=www.dabblebase.dev \
   --path=/openapi.json
   ```

### Create the `celeryworker` Celery Worker Application

1. First, we need to create the base app.

   ```
   oc new-app python:3.12~git@github.com:dabblebase/dabblebase.git#main \
   --source-secret=dabblebase-deploykey \
   --name=celeryworker \
   --strategy=docker
   ```

2. Then, specify the location of the API Dockerfile:

   ```
   oc patch buildconfig celeryworker --type=merge -p '{
       "spec": {
       "source": {
           "contextDir": "."
       },
       "strategy": {
           "dockerStrategy": {
               "dockerfilePath": "deploy/Dockerfile.celeryworker"
           }
       }
   }
   }'
   ```

   Then, set the secrets to the server secrets:

   ```
   oc set env deployment/celeryworker --from=secret/dabblebase-server-environment
   ```

   Finally, we rebuild the application.

   ```
   oc start-build celeryworker
   ```

   _Note: There is no need for services or routes since this runs internally only._

### Create the `celerybeat` Celery Beat Application

1. First, we need to create the base app.

   ```
   oc new-app python:3.12~git@github.com:dabblebase/dabblebase.git#main \
   --source-secret=dabblebase-deploykey \
   --name=celerybeat \
   --strategy=docker
   ```

2. Then, specify the location of the API Dockerfile:

   ```
   oc patch buildconfig celerybeat --type=merge -p '{
       "spec": {
       "source": {
           "contextDir": "."
       },
       "strategy": {
           "dockerStrategy": {
               "dockerfilePath": "deploy/Dockerfile.celerybeat"
           }
       }
   }
   }'
   ```

   Then, set the secrets to the server secrets:

   ```
   oc set env deployment/celerybeat --from=secret/dabblebase-server-environment
   ```

   Finally, we rebuild the application.

   ```
   oc start-build celerybeat
   ```

   _Note: There is no need for services or routes since this runs internally only._
