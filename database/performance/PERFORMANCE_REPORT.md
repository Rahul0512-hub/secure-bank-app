

\# SecureBank Database Performance Report



\## 1. Objective



Evaluate PostgreSQL query performance and verify whether the existing database indexes are being used effectively.



\## 2. Testing Environment



\- Database: PostgreSQL 16

\- Container: securebank-postgres

\- Database name: securebank

\- Testing tool: EXPLAIN ANALYZE

\- Storage engine: PostgreSQL



\## 3. Benchmark Dataset



Temporary benchmark records were generated using PostgreSQL `generate\_series()`.



| Table | Records generated |

|---|---:|

| Users | 1,000 |

| Accounts | 1,000 |

| Loans | 500 |

| Transactions | 10,000 |

| \*\*Total\*\* | \*\*12,500\*\* |



All benchmark records were rolled back after testing.



\## 4. Performance Test Results



| Test | Index used | Execution time |

|---|---|---:|

| Account lookup by user | idx\_accounts\_user\_id | 0.061 ms |

| Loan lookup by user | idx\_loans\_user\_id | 0.052 ms |

| Transactions by source account | idx\_transactions\_source\_account | 0.282 ms |

| Transactions by destination account | idx\_transactions\_destination\_account | 0.100 ms |

| Retrieve latest 20 transactions | idx\_transactions\_created\_at | 0.037 ms |



\## 5. Query Execution Analysis



\### Test 1: Account Lookup



\- PostgreSQL used an Index Scan.

\- Index: `idx\_accounts\_user\_id`

\- Execution time: 0.061 ms.



\### Test 2: Loan Lookup



\- PostgreSQL used an Index Scan.

\- Index: `idx\_loans\_user\_id`

\- Execution time: 0.052 ms.



\### Test 3: Source Account Transactions



\- PostgreSQL used a Bitmap Index Scan followed by a Bitmap Heap Scan.

\- Index: `idx\_transactions\_source\_account`

\- Execution time: 0.282 ms.



\### Test 4: Destination Account Transactions



\- PostgreSQL used a Bitmap Index Scan followed by a Bitmap Heap Scan.

\- Index: `idx\_transactions\_destination\_account`

\- Execution time: 0.100 ms.



\### Test 5: Recent Transactions



\- PostgreSQL used an Index Scan.

\- Index: `idx\_transactions\_created\_at`

\- Execution time: 0.037 ms.

\- The query retrieved the latest 20 transactions.



\## 6. Observations



1\. All five benchmark queries used their expected indexes.

2\. Account and loan lookups demonstrated low execution times.

3\. Source and destination transaction searches used bitmap index scans.

4\. The timestamp index supported efficient retrieval of recent transactions.

5\. No additional indexes were required based on this benchmark.



\## 7. Data Safety



The benchmark script used a database transaction with `BEGIN` and `ROLLBACK`.



All temporary test records were removed after execution. No permanent banking records were modified.



\## 8. Conclusion



The performance benchmark demonstrated that the existing PostgreSQL indexes were being used effectively for the tested queries.



All five queries completed in less than 1 millisecond in this test environment.



Further testing with larger datasets and concurrent workloads would be necessary before making production performance guarantees.



