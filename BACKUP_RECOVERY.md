\# SecureBank Database Backup and Recovery



\## 1. Overview



SecureBank provides PowerShell scripts to create PostgreSQL database backups and restore them into a separate database.



The backup uses PostgreSQL's custom archive format, which supports restoration through `pg\_restore`.



\## 2. Prerequisites



Ensure the following are installed and running:



\- Docker Desktop

\- Docker Compose

\- PostgreSQL Docker container: `securebank-postgres`

\- PowerShell

\- SecureBank project dependencies and database configuration



Start the database containers from the project directory:



```powershell

docker compose up -d

```



\## 3. Creating a Database Backup



Run the backup script:



```powershell

.\\database\\backup\\backup\_database.ps1

```



The script:



1\. Creates a `backups` directory if it does not exist.

2\. Generates a timestamped backup filename.

3\. Runs `pg\_dump` inside the PostgreSQL container.

4\. Copies the backup archive to the host machine.

5\. Removes the temporary backup from the container.

6\. Displays the backup file location and size.



Example output:



```text

Starting SecureBank database backup...



Backup completed successfully.

File: backups/securebank\_YYYYMMDD\_HHMMSS.dump

```



\## 4. Backup File Format



Backups use PostgreSQL custom format (`-Fc`).



Example:



```text

backups/

&#x20;   securebank\_YYYYMMDD\_HHMMSS.dump

```



Backup files are excluded from Git using `.gitignore` rules. They should be stored securely and not committed to the repository.



\## 5. Verifying a Backup



To inspect the contents of a backup archive, run:



```powershell

docker cp .\\backups\\securebank\_YYYYMMDD\_HHMMSS.dump securebank-postgres:/tmp/securebank\_check.dump

```



Then run:



```powershell

docker exec securebank-postgres pg\_restore --list /tmp/securebank\_check.dump

```



A valid archive should display its PostgreSQL archive contents, including tables, functions, indexes, constraints, and other database objects.



Replace the example filename with the actual backup filename.



\## 6. Restoring a Database Backup



The restore script restores a backup into a new database without overwriting the original `securebank` database.



Command:



```powershell

.\\database\\backup\\restore\_database.ps1 -BackupFile ".\\backups\\securebank\_YYYYMMDD\_HHMMSS.dump" -TargetDatabase "securebank\_recovery\_test"

```



The script:



1\. Validates the backup file.

2\. Checks that the PostgreSQL container is running.

3\. Validates the target database name.

4\. Refuses to overwrite an existing database.

5\. Prevents restoration into the original `securebank` database.

6\. Creates a new target database.

7\. Copies the backup into the PostgreSQL container.

8\. Executes `pg\_restore`.

9\. Removes temporary files.

10\. Removes the incomplete target database if restoration fails.



\## 7. Recovery Verification



After restoration, verify that all four tables exist and check their row counts:



```sql

SELECT 'users' AS table\_name, COUNT(\*) AS row\_count FROM users

UNION ALL

SELECT 'accounts', COUNT(\*) FROM accounts

UNION ALL

SELECT 'loans', COUNT(\*) FROM loans

UNION ALL

SELECT 'transactions', COUNT(\*) FROM transactions;

```



Verify that the fund transfer function exists:



```sql

SELECT proname

FROM pg\_proc

JOIN pg\_namespace ON pg\_namespace.oid = pg\_proc.pronamespace

WHERE nspname = 'public'

AND proname = 'transfer\_funds';

```



Compare the restored database with the backup's expected contents.



\## 8. Removing a Temporary Recovery Database



After verification, remove the temporary database:



```powershell

docker exec securebank-postgres psql -U securebank -d postgres -c "DROP DATABASE securebank\_recovery\_test;"

```



Only remove a database that was created specifically for recovery testing.



\## 9. Important Safety Considerations



\- Never commit database backup files to Git.

\- Keep backup files in a secure location.

\- Do not overwrite the original `securebank` database during recovery testing.

\- Do not delete Docker database volumes when performing routine backup or recovery operations.

\- Test restoration periodically.

\- Store production backups separately from the development machine.

\- `pg\_dump` backs up a database, not cluster-wide roles. Ensure the required database roles exist on the destination PostgreSQL cluster before restoring permissions.

\- The restore script is designed for a new, separate database. It does not replace an existing database.



\## 10. Project File Structure



```text

secure-bank-app/

│

├── database/

│   └── backup/

│       ├── backup\_database.ps1

│       └── restore\_database.ps1

│

├── backups/                  # Ignored by Git

│

├── .gitignore

└── BACKUP\_RECOVERY.md

```



\## 11. Testing Summary



The backup and recovery functionality was tested successfully.



| Test | Result |

|---|---|

| PostgreSQL backup creation | Passed |

| Backup archive inspection | Passed |

| Temporary database creation | Passed |

| Manual database restoration | Passed |

| Automated restore script | Passed |

| Restored table verification | Passed |

| Transfer function verification | Passed |

| Temporary database cleanup | Passed |



The tested backup restored all four tables and the `transfer\_funds` function successfully. The source database was not modified during recovery testing.



\## 12. Conclusion



The SecureBank project now includes database backup and recovery scripts using PostgreSQL `pg\_dump` and `pg\_restore`.



The implementation supports timestamped backups, archive inspection, safe restoration into a separate database, and post-restoration verification. These features provide a repeatable foundation for database recovery and data protection.

