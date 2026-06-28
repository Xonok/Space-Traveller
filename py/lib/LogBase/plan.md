A database based on storing changes to dictionaries into logs.

Immediate concerns:
*Create, delete, update a dictionary.
*Append to log.
*Read log from disk and redo operations.

Later:
*Schemas, validation, transactions, log rotation


Start with a pregenerated log.
For testing purposes, keep everything in the same folder for now and run this file alone.

**Issues**
- api.run requires explicit parameter names. (so does api.ask)

