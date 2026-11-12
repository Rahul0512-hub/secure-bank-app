const auditDb = db.getSiblingDB("securebank_audit");
const existingCollections = auditDb.getCollectionNames();

// 1. Create fraud_alerts collection
if (!existingCollections.includes("fraud_alerts")) {
    auditDb.createCollection("fraud_alerts", {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["user_id", "amount", "reason", "severity", "status", "created_at"],
                properties: {
                    transaction_id: { bsonType: ["int", "long", "null"] },
                    user_id: { bsonType: ["int", "long"] },
                    amount: { bsonType: ["double", "decimal", "int", "long"], minimum: 0 },
                    category: { bsonType: "string" },
                    reason: { bsonType: "string" },
                    severity: { bsonType: "string", enum: ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
                    status: { bsonType: "string", enum: ["OPEN", "INVESTIGATING", "RESOLVED", "DISMISSED"] },
                    created_at: { bsonType: "date" }
                }
            }
        },
        validationLevel: "strict",
        validationAction: "error"
    });
    print("Created fraud_alerts collection.");
}

auditDb.fraud_alerts.createIndex(
    { severity: 1, created_at: -1 },
    { name: "idx_fraud_severity_time" }
);

// 2. Create login_events collection
if (!existingCollections.includes("login_events")) {
    auditDb.createCollection("login_events", {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: ["email", "status", "occurred_at"],
                properties: {
                    user_id: { bsonType: ["int", "long", "null"] },
                    email: { bsonType: "string" },
                    ip_address: { bsonType: "string" },
                    user_agent: { bsonType: "string" },
                    status: { bsonType: "string", enum: ["SUCCESS", "FAILED", "LOCKED"] },
                    occurred_at: { bsonType: "date" }
                }
            }
        },
        validationLevel: "strict",
        validationAction: "error"
    });
    print("Created login_events collection.");
}

auditDb.login_events.createIndex(
    { email: 1, occurred_at: -1 },
    { name: "idx_login_email_time" }
);

print("Person B MongoDB collections (fraud_alerts, login_events) setup completed.");