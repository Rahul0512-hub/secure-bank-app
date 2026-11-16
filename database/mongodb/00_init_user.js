// ============================================================
// SecureBank: MongoDB Application User Setup
// File: database/mongodb/00_init_user.js
// Purpose: Automatically creates the application user during
//          initial container startup in docker-entrypoint-initdb.d.
// ============================================================

const auditDb = db.getSiblingDB("securebank_audit");

const users = auditDb.getUsers();
const userExists = users.some(u => u.user === "securebank_audit_app");

if (!userExists) {
    auditDb.createUser({
        user: "securebank_audit_app",
        pwd: "SecureBankDev_AuditPassword_123",
        roles: [
            { role: "readWrite", db: "securebank_audit" }
        ]
    });
    print("Created MongoDB application user: securebank_audit_app");
} else {
    print("MongoDB application user securebank_audit_app already exists.");
}
