# Deployment Steps

This is a catalog of the deployment steps needed to run Dabblebase on Carolina CloudApps.

### Part 1: Log into OC Terminal

To log into the `OC` terminal interface, access the terminal in the devcontainer.

Look in the top right in the CloudApps console and click on the username, click the drop down, and select “Copy Login Command”. From here select “Display Token”. Here, look for the line “Log in with this token” and copy the complete command beginning with oc login to your clipboard.

```
oc login <token here>
```

### Part 2: Create Databases and Redis Cluster

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

### Part 3: Create Secrets

1. Create a generic secret called `dabblebase-server-environment` using this command:

   ```
   oc create secret generic dabblebase-server-environment \
    --from-literal=KEY=value \
    ...
   ```

   Add key-value pairs for every environment variable in `/server/.env`. Use the information for the databases by finding the generated secrets for the database in OpenShift. Make sure that the port for the database is `5433` and `5434` respectively. For all passwords, generate the password in the DevContainer terminal using the command:

   ```
   openssl rand -hex 32
   ```

2. Create a generic secret called `dabblebase-realtime-environment` using this command:

   ```
   oc create secret generic dabblebase-realtime-environment \
    --from-literal=KEY=value \
    ...
   ```

   Add key-value pairs for every environment variable in `/server/.env`. Use the information for the databases by finding the generated secrets for the database in OpenShift and the passwords generated in step 1.

### Part 4: Create DeployKey to Link GitHub Repo to OpenShift

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

### Part 5: Create the Applications
