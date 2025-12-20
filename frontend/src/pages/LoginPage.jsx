import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import toast from 'react-hot-toast';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};

    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);
    setErrors({});
    
    try {
      const response = await login(formData.username, formData.password);
      
      if (response && response.access_token) {
        toast.success('Login successful! Redirecting...');
        
        // Always redirect to assistant page after login (default landing page)
        const redirectPath = '/assistant';
        
        setTimeout(() => {
          window.location.href = redirectPath;
        }, 500);
      } else {
        toast.error('Login failed: Invalid response from server');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      let message = 'Login failed. Please try again.';
      
      if (error.response) {
        if (error.response.status === 401) {
          message = 'Incorrect username or password';
        } else if (error.response.status === 403) {
          message = 'Account is inactive. Please contact administrator.';
        } else if (error.response.data) {
          if (typeof error.response.data === 'string') {
            message = error.response.data;
          } else if (error.response.data.detail) {
            if (typeof error.response.data.detail === 'string') {
              message = error.response.data.detail;
            } else if (Array.isArray(error.response.data.detail)) {
              message = error.response.data.detail.map(err => err.msg || err).join(', ');
            }
          }
        }
      } else if (error.request) {
        message = 'Cannot connect to server. Please check your connection.';
      }
      
      toast.error(message, { duration: 4000 });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              DITA AI Assistant
            </h1>
            <p className="text-slate-600">Multi-Role Authentication System</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              error={errors.username}
              required
              autoFocus
              placeholder="Enter your username"
            />

            <div>
              <Input
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                required
                placeholder="Enter your password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-700"
              >
                {showPassword ? 'Hide' : 'Show'} password
              </button>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              Login
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-600">
            <p>Authorized personnel only</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
