const auditDb = db.getSiblingDB("securebank_audit");
const collection = auditDb.transaction_audit_logs;

const testId = NumberLong("999991");
let passed = 0;
let failed = 0;

function test(name, callback) {
    try {
        callback();
        print("PASS: " + name);
        passed++;
    } catch (error) {
        print("FAIL: " + name + " - " + error.message);
        failed++;
    }
}

try {
    test("Accepts a valid audit event", () => {
        const result = collection.insertOne({
            transaction_id: testId,
            event_type: "TRANSFER_COMPLETED",
            status: "SUCCESS",
            source_account_id: NumberLong("1001"),
            destination_account_id: NumberLong("1002"),
            amount: NumberDecimal("1250.00"),
            currency: "INR",
            occurred_at: new Date(),
            description: "Automated validation test"
        });

        if (!result.acknowledged) {
            throw new Error("Insert was not acknowledged");
        }
    });

    test("Rejects an invalid event type", () => {
        let rejected = false;

        try {
            collection.insertOne({
                transaction_id: NumberLong("999992"),
                event_type: "INVALID_EVENT",
                status: "SUCCESS",
                occurred_at: new Date()
            });
        } catch (error) {
            if (error.code === 121) {
                rejected = true;
            } else {
                throw error;
            }
        }

        if (!rejected) {
            throw new Error("Invalid event type was accepted");
        }
    });

    test("Rejects a document missing required fields", () => {
        let rejected = false;

        try {
            collection.insertOne({
                transaction_id: NumberLong("999993"),
                event_type: "TRANSFER_COMPLETED"
            });
        } catch (error) {
            if (error.code === 121) {
                rejected = true;
            } else {
                throw error;
            }
        }

        if (!rejected) {
            throw new Error("Incomplete document was accepted");
        }
    });
} finally {
    collection.deleteMany({
        transaction_id: {
            $in: [
                NumberLong("999991"),
                NumberLong("999992"),
                NumberLong("999993")
            ]
        }
    });
}

print(" ");
print("MongoDB Audit Tests: " + passed + " passed, " + failed + " failed.");

if (failed > 0) {
    quit(1);
}
