A database based on storing changes to dictionaries into logs.

Immediate concerns:
*Create, delete, update a dictionary.

Later:
*Schemas, validation, transactions, log rotation


Start with a pregenerated log.
For testing purposes, keep everything in the same folder for now and run this file alone.

**Issues**
- When there is an error during testing, the rollback isn't done. It seems having any operation fail with an error is unacceptable.

