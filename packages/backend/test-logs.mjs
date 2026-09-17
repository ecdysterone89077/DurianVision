async function run() {
  try {
    const loginRes = await fetch('http://localhost:3005/api/auth/sign-in/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Origin': 'http://localhost:5173' },
      body: JSON.stringify({ email: 'faunas@gmail.com', password: 'faunas123' })
    });
    const cookie = loginRes.headers.get('set-cookie');
    console.log('Fetching logs with cookie...');
    const logsRes = await fetch('http://localhost:3005/api/logs?limit=5', {
      headers: { 'Cookie': cookie, 'Origin': 'http://localhost:5173' }
    });
    console.log('Logs:', await logsRes.json());
  } catch(e) { console.error(e) }
}; run();
