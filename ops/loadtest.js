import http from 'k6/http';
import { sleep } from 'k6';

const BASE_URL = 'https://calculator.com';

export const options = {
	scenarios: {
		increase_load: {
			executor: 'ramping-vus',
			startVUs: 10,
			stages: [
				{ duration: '30s', target: 10 }, // Start with 10 users
				{ duration: '30s', target: 20 }, // Increase to 20 users
				{ duration: '30s', target: 30 }, // Increase to 30 users
				{ duration: '30s', target: 40 }, // Increase to 40 users
				{ duration: '30s', target: 50 }, // Increase to 50 users
				{ duration: '30s', target: 60 }, // Increase to 60 users
				{ duration: '30s', target: 70 }, // Increase to 70 users
				{ duration: '30s', target: 80 }, // Increase to 80 users
				{ duration: '30s', target: 90 }, // Increase to 90 users
				{ duration: '30s', target: 100 } // Increase to 100 users
			]
		}
	}
};