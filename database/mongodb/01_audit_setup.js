const auditDb = db.getSiblingDB("securebank_audit");

const collectionName = "transaction_audit_logs";
const existingCollections = auditDb.getCollectionNames();

if (!existingCollections.includes(collectionName)) {
    auditDb.createCollection(collectionName, {
        validator: {
            $jsonSchema: {
                bsonType: "object",
                required: [
                    "transaction_id",
                    "event_type",
                    "status",
                    "occurred_at"
                ],
                properties: {
                    transaction_id: {
                        bsonType: ["int", "long"],
                        description: "PostgreSQL transaction ID"
                    },
                    event_type: {
                        bsonType: "string",
                        enum: [
                            "TRANSFER_INITIATED",
                            "TRANSFER_COMPLETED",
                            "TRANSFER_FAILED"
                        ]
                    },
                    status: {
                        bsonType: "string",
                        enum: ["SUCCESS", "FAILED", "PENDING"]
                    },
                    source_account_id: {
                        bsonType: ["int", "long"]
                    },
                    destination_account_id: {
                        bsonType: ["int", "long"]
                    },
                    amount: {
                        bsonType: "decimal",
                        minimum: 0
                    },
                    currency: {
                        bsonType: "string"
                    },
                    occurred_at: {
                        bsonType: "date"
                    },
                    actor_user_id: {
                        bsonType: ["int", "long"]
                    },
                    description: {
                        bsonType: "string"
                    }
                }
            }
        },
        validationLevel: "strict",
        validationAction: "error"
    });

    print("Created transaction_audit_logs collection.");
} else {
    print("transaction_audit_logs collection already exists; skipping creation.");
}

auditDb.transaction_audit_logs.createIndex(
    { transaction_id: 1, occurred_at: -1 },
    { name: "idx_audit_transaction_time" }
);

auditDb.transaction_audit_logs.createIndex(
    { event_type: 1, occurred_at: -1 },
    { name: "idx_audit_event_time" }
);

print("MongoDB audit setup completed.");
