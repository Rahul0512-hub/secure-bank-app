

\# MongoDB Transaction Audit Logging



\## 1. Overview



MongoDB stores supplementary transaction audit events for the SecureBank application.



PostgreSQL remains the primary source of truth for banking transactions and account balances. MongoDB stores audit information separately.



\## 2. Database Configuration



\- Database: `securebank\_audit`

\- Collection: `transaction\_audit\_logs`

\- Application user: `securebank\_audit\_app`

\- Authentication database: `securebank\_audit`

\- Access role: `readWrite` on `securebank\_audit`



The application user is separate from the MongoDB root administrator.



\## 3. Audit Event Structure



| Field | BSON Type | Description |

|---|---|---|

| transaction\_id | int / long | PostgreSQL transaction ID |

| event\_type | string | Type of transaction event |

| status | string | Event outcome |

| source\_account\_id | int / long | Source account ID |

| destination\_account\_id | int / long | Destination account ID |

| amount | decimal | Transaction amount |

| currency | string | Transaction currency |

| occurred\_at | date | Event timestamp |

| actor\_user\_id | int / long | User who initiated the action |

| description | string | Additional event information |



Required fields:

\- `transaction\_id`

\- `event\_type`

\- `status`

\- `occurred\_at`



\## 4. Allowed Values



Event types:

\- `TRANSFER\_INITIATED`

\- `TRANSFER\_COMPLETED`

\- `TRANSFER\_FAILED`



Statuses:

\- `SUCCESS`

\- `FAILED`

\- `PENDING`



MongoDB uses strict schema validation and rejects invalid documents.



\## 5. Indexes



| Index | Fields | Purpose |

|---|---|---|

| idx\_audit\_transaction\_time | transaction\_id, occurred\_at descending | Retrieve events for a transaction |

| idx\_audit\_event\_time | event\_type, occurred\_at descending | Filter events by type and time |

| \_id\_ | \_id | MongoDB default document identifier |



\## 6. Setup



Reusable setup script:



`database/mongodb/01\_audit\_setup.js`



Copy it into the running MongoDB container:



```powershell

docker cp database\\mongodb\\01\_audit\_setup.js securebank-mongodb:/tmp/01\_audit\_setup.js

```



Run it using the application account:



```powershell

docker exec -it securebank-mongodb mongosh --username securebank\_audit\_app --authenticationDatabase securebank\_audit --password --file /tmp/01\_audit\_setup.js

```



Enter the application user's password when prompted.



The script creates the collection if it does not exist and ensures both indexes are present.



\## 7. Automated Tests



Test script:



`database/mongodb/02\_audit\_tests.js`



Copy and execute it:



```powershell

docker cp database\\mongodb\\02\_audit\_tests.js securebank-mongodb:/tmp/02\_audit\_tests.js



docker exec -it securebank-mongodb mongosh --username securebank\_audit\_app --authenticationDatabase securebank\_audit --password --file /tmp/02\_audit\_tests.js

```



The tests verify:

1\. Valid audit event insertion.

2\. Rejection of an invalid event type.

3\. Rejection of documents missing required fields.

4\. Automatic cleanup of test records.



\## 8. Verification



Check collection indexes:



```javascript

db.transaction\_audit\_logs.getIndexes()

```



Check the number of stored audit events:



```javascript

db.transaction\_audit\_logs.countDocuments()

```



\## 9. Security and Consistency Notes



\- The root administrator account must not be used by the application.

\- The application uses a dedicated MongoDB account.

\- Database credentials must remain in the local `.env` file and must not be committed.

\- PostgreSQL remains authoritative for account balances and transaction records.

\- MongoDB audit logging is supplementary and does not create a distributed atomic transaction with PostgreSQL.

\- Future application integration should use a reliable outbox/retry mechanism so audit events can be delivered even if MongoDB is temporarily unavailable.



\## 10. Current Implementation Scope



This feature establishes the MongoDB audit database, collection validation, indexes, reusable setup script, and automated validation tests.



Application-level event generation and integration with the PostgreSQL transfer function are future work.



