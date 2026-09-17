import { auth } from './src/auth/index.js'; auth.api.signUpEmail({ body: { name: 't', email: 'test3@test.com', password: 'password123' } }).then(console.log).catch(console.error);
