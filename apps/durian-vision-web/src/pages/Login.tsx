import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signIn, authClient } from '../lib/auth';

export default function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignUp) {
        const { error: signUpError } = await authClient.signUp.email({
          email,
          password,
          name: name || 'Admin',
        });
        if (signUpError) {
          setError(signUpError.message || 'Sign up failed');
          setLoading(false);
          return;
        }
        navigate('/dashboard');
        return;
      }

      const { error: authError } = await signIn.email({
        email,
        password,
      });

      if (authError) {
        setError(authError.message || 'Login failed');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-16 h-16 rounded-xl bg-primary flex items-center justify-center text-on-primary shadow-[0_0_24px_rgba(75,226,119,0.3)] mb-4 border border-outline-variant">
          <span className="material-symbols-outlined text-[32px]" style={{ fontVariationSettings: "'FILL' 1" }}>dataset</span>
        </div>
        <h2 className="mt-2 text-center font-headline-md text-headline-md font-bold text-primary dark:text-primary">DurianVision</h2>
        <p className="mt-2 text-center text-on-surface-variant">{isSignUp ? 'Create a local account' : 'Sign in to your AI Engine'}</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-surface-container py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-outline-variant glass-card">
          <form className="space-y-6" onSubmit={handleSubmit}>
            
            {isSignUp && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-on-surface">Name</label>
                <div className="mt-1">
                  <input 
                    id="name" 
                    type="text" 
                    className="appearance-none block w-full px-3 py-2 border border-outline rounded-md shadow-sm placeholder-on-surface-variant focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-surface-dim text-on-surface" 
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-on-surface">Email address</label>
              <div className="mt-1">
                <input 
                  id="email" 
                  type="email" 
                  required 
                  className="appearance-none block w-full px-3 py-2 border border-outline rounded-md shadow-sm placeholder-on-surface-variant focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-surface-dim text-on-surface" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-on-surface">Password</label>
              <div className="mt-1">
                <input 
                  id="password" 
                  type="password" 
                  required 
                  className="appearance-none block w-full px-3 py-2 border border-outline rounded-md shadow-sm placeholder-on-surface-variant focus:outline-none focus:ring-primary focus:border-primary sm:text-sm bg-surface-dim text-on-surface"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="text-error text-sm mt-2">{error}</div>
            )}

            <div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-on-primary bg-primary hover:bg-primary-fixed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
              >
                {loading ? 'Processing...' : (isSignUp ? 'Create Account' : 'Sign In')}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <button 
              type="button" 
              className="text-sm text-primary hover:text-primary-fixed font-medium"
              onClick={() => setIsSignUp(!isSignUp)}
            >
              {isSignUp ? 'Already have an account? Sign In' : 'First time? Create a local account'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
