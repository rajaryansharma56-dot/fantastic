
const API_BASE_URL = "http://127.0.0.1:8000";

// Fetch all machines
export async function getMachines() {
    const response = await fetch(`${API_BASE_URL}/machines/`);

    if (!response.ok) {
        throw new Error("Failed to fetch machines");
    }

    return await response.json();
}

// Register a new machine
export async function createMachine(machine) {
    const response = await fetch(`${API_BASE_URL}/machines/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(machine),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Failed to register machine");
    }

    return data;
}


// Fetch risk assessments for all machines
export async function getMachineRisks() {
    const response = await fetch(`${API_BASE_URL}/api/risk/`);

    if (!response.ok) {
        throw new Error("Failed to fetch machine risk assessments");
    }

    return await response.json();
}
