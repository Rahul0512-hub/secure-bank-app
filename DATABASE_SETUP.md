# SecureBank Database Setup Guide



This guide explains how to configure the SecureBank database environment locally using Docker Compose, PostgreSQL with pgvector, and MongoDB.



## 1. Prerequisites



Install the following software:



- Git

- Docker Desktop

- Docker Compose v2 (included with Docker Desktop)

- A code editor such as VS Code



Make sure Docker Desktop is running before continuing.



## 2. Clone the Repository



```bash

git clone https://github.com/Rahul0512-hub/secure-bank-app.git

cd secure-bank-app

```



## 3. Configure Environment Variables



Create your local environment file from the example:



*\*Windows PowerShell:\*\*



```powershell

Copy-Item .env.example .env

```



Open `.env` and replace the example values with your own development credentials.



The environment variables are:



| Variable | Description |

|---|---|

| `POSTGRES\_PASSWORD` | PostgreSQL administrator password |

| `MONGO\_ROOT\_USERNAME` | MongoDB administrator username |

| `MONGO\_ROOT\_PASSWORD` | MongoDB administrator password |

| `DATABASE\_URL` | PostgreSQL connection URL for the application login |



Configure `DATABASE\_URL` using the password assigned to `securebank\_app\_login`.



Example format:



```text

DATABASE\_URL=postgresql://securebank\_app\_login:YOUR\_PASSWORD@localhost:5432/securebank

```



If the password contains special characters, URL-encode them in the connection URL.



*\*Security:\*\* Never commit `.env` or share actual database credentials. Only `.env.example` should be committed.



## 4. Start the Database Containers



Start PostgreSQL and MongoDB:



```bash

docker compose up -d

```



Check container status:



```bash

docker compose ps

```



Both database containers should become healthy.



The configured services are:



| Database | Container | Port |

|---|---|---|

| PostgreSQL with pgvector | `securebank-postgres` | `5432` |

| MongoDB 7 | `securebank-mongodb` | `27017` |



Docker volumes preserve database data between container restarts.



## 5. PostgreSQL Automatic Initialization



The Docker Compose configuration mounts:



```text

./database/init

```



into:



```text

/docker-entrypoint-initdb.d

```



During the first initialization of a fresh PostgreSQL data directory, the following scripts execute automatically:



1\. `database/init/01\_schema.sql` â€” creates the database schema, tables, constraints, indexes, and required extension.

2\. `database/init/02\_transfer\_funds.sql` â€” creates the atomic fund transfer function.



*\*Important:\*\* PostgreSQL initialization scripts execute automatically only when the database data directory is initialized for the first time. Restarting existing containers does not rerun them.



Do not remove Docker volumes to rerun initialization unless you intentionally want to delete the stored database data.



## 6. Configure Database Security



The security scripts must be executed manually after PostgreSQL initialization.



### Step 1: Configure database roles and permissions



Copy the SQL file into the PostgreSQL container:



```powershell

docker cp database/security/01\_roles\_and\_permissions.sql securebank-postgres:/tmp/01\_roles\_and\_permissions.sql

```



Execute it:



```powershell

docker exec -it securebank-postgres psql -U securebank -d securebank -f /tmp/01\_roles\_and\_permissions.sql

```



This creates the application permission group and transfer permission role, configures the required privileges, and assigns ownership of the transfer function.



### Step 2: Create the application login role



Copy the script:



```powershell

docker cp database/security/02\_app\_login\_role.sql securebank-postgres:/tmp/02\_app\_login\_role.sql

```



Execute it:



```powershell

docker exec -it securebank-postgres psql -U securebank -d securebank -f /tmp/02\_app\_login\_role.sql

```



This creates or updates `securebank\_app\_login` and grants it membership in `securebank\_app`.



### Step 3: Set the application login password



Open the PostgreSQL administrator console:



```powershell

docker exec -it securebank-postgres psql -U securebank -d securebank

```



Run:



```sql

\\password securebank\_app\_login

```



Enter and confirm a strong password when prompted.



Exit:



```sql

\\q

```



The password is deliberately not stored in the SQL setup script.



### Step 4: Configure the application connection URL



Update `DATABASE\_URL` in your local `.env` file using the password you just configured.



Do not commit this file.



## 7. Verify the Application Login



Test the application login:



```powershell

docker exec -it securebank-postgres psql -U securebank\_app\_login -d securebank -W

```



Enter the password when prompted.



Check the connected role:



```sql

SELECT current\_user;

```



The expected result is:



```text

securebank\_app\_login

```



Check the permissions:



```sql

SELECT

&#x20;   has\_table\_privilege(current\_user, 'public.accounts', 'SELECT') AS can\_read\_accounts,

&#x20;   has\_table\_privilege(current\_user, 'public.accounts', 'UPDATE') AS can\_update\_accounts,

&#x20;   has\_table\_privilege(current\_user, 'public.transactions', 'INSERT') AS can\_insert\_transactions,

&#x20;   has\_function\_privilege(

&#x20;       current\_user,

&#x20;       'public.transfer\_funds(bigint,bigint,numeric,character varying,text)',

&#x20;       'EXECUTE'

&#x20;   ) AS can\_execute\_transfer;

```



Expected results:



| Permission | Expected |

|---|---|

| Read accounts | `true` |

| Directly update accounts | `false` |

| Directly insert transactions | `false` |

| Execute fund transfer function | `true` |



Exit the PostgreSQL console:



```sql

\\q

```



## 8. Run Automated SQL Tests



The fund transfer test script is located at:



```text

database/tests/test\_transfer\_funds.sql

```



Copy it into the PostgreSQL container:



```powershell

docker cp database/tests/test\_transfer\_funds.sql securebank-postgres:/tmp/test\_transfer\_funds.sql

```



Execute the tests:



```powershell

docker exec -it securebank-postgres psql -U securebank -d securebank -f /tmp/test\_transfer\_funds.sql

```



The test script checks eight scenarios:



1\. Successful fund transfer.

2\. Insufficient balance.

3\. Zero transfer amount.

4\. Negative transfer amount.

5\. Same source and destination account.

6\. Non-existent source account.

7\. Inactive source account.

8\. Empty transaction type.



The test script uses a transaction and rolls back its test data.



A successful run displays:



```text

ALL 8 FUND TRANSFER TESTS PASSED

```



## 9. Database Directory Structure



```text

database/

â”‚

â”œâ”€â”€ init/

â”‚   â”œâ”€â”€ 01\_schema.sql

â”‚   â””â”€â”€ 02\_transfer\_funds.sql

â”‚

â”œâ”€â”€ functions/

â”‚   â””â”€â”€ 02\_transfer\_funds.sql

â”‚

â”œâ”€â”€ security/

â”‚   â”œâ”€â”€ 01\_roles\_and\_permissions.sql

â”‚   â””â”€â”€ 02\_app\_login\_role.sql

â”‚

â””â”€â”€ tests/

&#x20;   â””â”€â”€ test\_transfer\_funds.sql

```



## 10. Useful Docker Commands



Check running containers:



```powershell

docker compose ps

```



View PostgreSQL logs:



```powershell

docker logs securebank-postgres

```



View MongoDB logs:



```powershell

docker logs securebank-mongodb

```



Stop containers without deleting database data:



```powershell

docker compose down

```



Start them again:



```powershell

docker compose up -d

```



*\*Warning:\*\* Avoid `docker compose down -v` unless you intentionally want to delete the persistent database volumes and all data stored in them.



## 11. Troubleshooting



| Problem | Suggested solution |

|---|---|

| Docker connection error | Start Docker Desktop and retry. |

| PostgreSQL is not healthy | Check `docker logs securebank-postgres`. |

| Port 5432 is already in use | Stop the other PostgreSQL service or resolve the port conflict. |

| Application login fails | Verify the login role exists and its password is correct. |

| Permission denied | Execute the security scripts in the documented order. |

| Initialization scripts did not execute | Check whether the PostgreSQL data volume already existed. |

| Connection URL fails | Check the username, password, host, port, database name, and URL encoding. |



---



*\*End of Database Setup Guide\*\*
