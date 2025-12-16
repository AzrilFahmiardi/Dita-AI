# FRONTEND AUTH UI DESIGN - PHASE 5

**Project:** Dita AI Assistant - Frontend Dashboard  
**Date Created:** 2025-12-16  
**Branch:** feature/frontend-auth  
**Status:** IN PROGRESS - Phase 5.1-5.3 COMPLETE, Phase 5.4-5.6 PENDING

---

## 🎯 OVERVIEW

Web dashboard untuk management dan monitoring sistem Dita dengan 3 role berbeda:
- **KAPOLRI**: Full access (user management, contact management, audit logs)
- **KAPOLDA**: Limited access (view users, manage contacts, limited audit logs)
- **KAPOLRES**: Minimal access (view profile, view contacts, own activity logs)

---

## ⚠️ MANDATORY CODE STANDARDS

**This project requires professional, production-ready code:**

1. **NO EMOJIS** - Never use emojis in code, comments, or logs
2. **Professional Naming** - Use clear, descriptive, industry-standard names
3. **Minimal Comments** - Comment only when necessary, always professional tone
4. **Clean Code** - Follow established patterns, no hacks or shortcuts
5. **White-Dominant Design** - Professional color scheme with minimal accent colors

**Code Quality Checklist:**
- [x] No emojis in any code files
- [x] All variables/functions have descriptive names
- [x] Comments are professional and add value
- [x] JSDoc for all exported functions
- [x] Consistent formatting throughout
- [ ] No console.log in production code (dev mode only)
- [x] Error handling on all async operations

---

### Color Scheme (Professional & Clean)

**Primary Palette:**
```css
Background:
- Primary Background: #FFFFFF (white)
- Secondary Background: #F8FAFC (slate-50) - subtle gray
- Card Background: #FFFFFF with border

Accent Color (Main):
- Primary: #2563EB (blue-600) - professional blue
- Primary Hover: #1D4ED8 (blue-700)
- Primary Light: #DBEAFE (blue-100) - for highlights

Text:
- Primary Text: #0F172A (slate-900) - near black
- Secondary Text: #64748B (slate-500) - muted gray
- Disabled Text: #CBD5E1 (slate-300)

Borders:
- Default Border: #E2E8F0 (slate-200)
- Focus Border: #2563EB (blue-600)
- Divider: #F1F5F9 (slate-100)

Status Colors (Functional only):
- Success: #10B981 (emerald-500)
- Success Light: #D1FAE5 (emerald-100)
- Warning: #F59E0B (amber-500)
- Warning Light: #FEF3C7 (amber-100)
- Error: #EF4444 (red-500)
- Error Light: #FEE2E2 (red-100)
- Info: #3B82F6 (blue-500)
- Info Light: #DBEAFE (blue-100)

Shadows:
- Subtle: 0 1px 2px 0 rgb(0 0 0 / 0.05)
- Medium: 0 4px 6px -1px rgb(0 0 0 / 0.1)
- Large: 0 10px 15px -3px rgb(0 0 0 / 0.1)
```

**Design Philosophy:**
- White dominance: Clean, professional, spacious
- Single accent color: Blue for consistency
- Minimal color usage: Only functional states use color
- High contrast text: Excellent readability
- Subtle shadows: Depth without distraction*Status:** 📐 PLANNING

---

## 🎯 OVERVIEW

Web dashboard untuk management dan monitoring sistem Dita dengan 3 role berbeda:
- **KAPOLRI**: Full access (user management, contact management, audit logs)
- **KAPOLDA**: Limited access (view users, manage contacts, limited audit logs)
- **KAPOLRES**: Minimal access (view profile, view contacts, own activity logs)

---

## CODE STANDARDS & BEST PRACTICES

### Professional Code Requirements

**1. NO EMOJIS in Code:**
```javascript
// ❌ WRONG - Do not use emojis
const handleSubmit = () => {
  console.log('✅ Form submitted successfully!');
  toast.success('🎉 User created!');
};

// ✅ CORRECT - Clean professional code
const handleSubmit = () => {
  console.log('Form submitted successfully');
  toast.success('User created successfully');
};
```

**2. Professional Naming Conventions:**
```javascript
// ❌ WRONG - Informal, unclear names
const stuff = [];
const doThing = () => {};
const x = getUserData();
const temp = 'value';

// ✅ CORRECT - Clear, descriptive, professional names
const users = [];
const fetchUserList = () => {};
const currentUser = getUserData();
const temporaryToken = 'value';
```

**3. Comments: Professional & Sufficient (Not Excessive):**
```javascript
// ❌ WRONG - Too many obvious comments
// This function adds two numbers together
// Takes two parameters: a and b
// Returns the sum of a and b
const add = (a, b) => {
  // Return a plus b
  return a + b; // Return the result
};

// ❌ WRONG - Informal comments
// Let's grab all the users lol
// TODO: fix this mess later
// This is hacky but whatever

// ✅ CORRECT - Professional, sufficient comments
/**
 * Fetch users with role-based filtering
 * @param {string} role - User role filter
 * @returns {Promise<Array>} Filtered user list
 */
const fetchUsers = async (role) => {
  // Apply role filter if provided
  const params = role ? { role } : {};
  return await userService.getUsers(params);
};

// ✅ CORRECT - Comment only when necessary
const handleDelete = async (id) => {
  // Optimistic update: remove from UI immediately
  setUsers(users.filter(u => u.id !== id));
  
  try {
    await userService.deleteUser(id);
  } catch (error) {
    // Revert UI on failure
    setUsers(previousUsers);
    toast.error('Failed to delete user');
  }
};
```

**4. Consistent Code Style:**
```javascript
// ✅ Use consistent formatting
const UserCard = ({ user, onEdit, onDelete }) => {
  const { id, username, role, isActive } = user;
  
  return (
    <div className="card">
      <h3>{username}</h3>
      <p>{role}</p>
      <button onClick={() => onEdit(id)}>Edit</button>
      <button onClick={() => onDelete(id)}>Delete</button>
    </div>
  );
};

// ✅ Use consistent error handling
try {
  await performAction();
} catch (error) {
  handleApiError(error);
}
```

**5. Clean, Readable Code Structure:**
```javascript
// ✅ Group related logic
const UserManagement = () => {
  // State declarations
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  
  // Custom hooks
  const { user: currentUser } = useAuth();
  
  // Effects
  useEffect(() => {
    fetchUsers();
  }, [filters]);
  
  // Event handlers
  const handleCreate = async (userData) => {
    // Implementation
  };
  
  const handleUpdate = async (id, userData) => {
    // Implementation
  };
  
  const handleDelete = async (id) => {
    // Implementation
  };
  
  // Render
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

---

## SYSTEM DESIGN PRINCIPLES

### 1. Code Organization

**Directory Structure Rationale:**
```
src/
├── components/     # Reusable UI components (atomic design)
├── pages/         # Route-level components
├── services/      # API layer (business logic isolation)
├── contexts/      # Global state management
├── hooks/         # Custom React hooks (logic reuse)
├── utils/         # Pure functions (no side effects)
├── routes/        # Route configuration (centralized)
└── config/        # Environment configuration
```

**Naming Conventions:**
```javascript
// Components: PascalCase
components/common/Button.jsx
components/forms/UserForm.jsx

// Hooks: camelCase with 'use' prefix
hooks/useAuth.js
hooks/useUsers.js

// Services: camelCase with service suffix
services/auth.service.js
services/user.service.js

// Utils: camelCase descriptive names
utils/formatters.js
utils/validators.js

// Constants: UPPER_SNAKE_CASE
utils/constants.js: API_BASE_URL, TOKEN_KEY

// CSS Classes: kebab-case (Tailwind convention)
className="btn-primary"
className="card-header"
```

### 2. Component Architecture

**Atomic Design Pattern:**
```
Atoms (Smallest):
- Button, Input, Badge, Icon
- No business logic
- Pure presentational

Molecules (Combined Atoms):
- FormField (Label + Input + Error)
- SearchBar (Input + Icon + Button)
- Basic business logic

Organisms (Complex Components):
- DataTable, UserForm, Sidebar
- Contain state management
- API integration

Templates (Page Layouts):
- DashboardLayout, AuthLayout
- Composition of organisms
- No data fetching

Pages (Routes):
- Dashboard, UserManagement
- Data fetching
- Route-specific logic
```

**Component File Structure:**
```javascript
// components/common/Button.jsx

/**
 * Primary button component following design system
 * @param {string} variant - Button style: primary | secondary | ghost
 * @param {string} size - Button size: sm | md | lg
 * @param {boolean} disabled - Disabled state
 * @param {function} onClick - Click handler
 * @param {ReactNode} children - Button content
 */
const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  onClick,
  children,
  ...props 
}) => {
  // IMPORTANT: Use inline-flex for proper icon+text alignment
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors';
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-white text-slate-700 border border-slate-300',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100'
  };
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]}`}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
```

**Button with Icon - Best Practices:**
```javascript
// ❌ WRONG - Icon and text may stack vertically
<Button>
  <PlusIcon className="w-4 h-4 mr-2" />
  Create User
</Button>

// ✅ CORRECT - Use span wrapper for proper flex layout
<Button>
  <PlusIcon className="w-4 h-4" />
  <span className="ml-2">Create User</span>
</Button>

// ✅ CORRECT - Icon-only button (no text needed)
<button className="p-1 text-blue-600 hover:text-blue-800">
  <PencilIcon className="w-5 h-5" />
</button>
```

**Dropdown/Select - Best Practices:**
```javascript
// ✅ CORRECT - Proper padding and arrow positioning
<select className="px-3 py-2 pr-10 border border-slate-300 rounded-lg">
  <option value="">All Roles</option>
  <option value="KAPOLRI">KAPOLRI</option>
  <option value="KAPOLDA">KAPOLDA</option>
</select>

// Key points:
// - px-3: Horizontal padding (left and right)
// - py-2: Vertical padding
// - pr-10: Extra right padding for dropdown arrow
// - This prevents text from overlapping with arrow icon
```

### 3. State Management Strategy

**Three-Tier State:**
```javascript
// 1. Server State (API data)
// Managed by custom hooks
const useUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return { users, loading, error, fetchUsers };
};

// 2. Global State (auth, theme)
// Managed by Context API
const AuthContext = createContext();

// 3. Local State (forms, UI)
// Managed by useState in components
const [isOpen, setIsOpen] = useState(false);
```

**State Update Patterns:**
```javascript
// Immutable updates
setUsers(prevUsers => [...prevUsers, newUser]);
setUser(prevUser => ({ ...prevUser, name: newName }));

// Optimistic updates
const deleteUser = async (id) => {
  // Update UI immediately
  setUsers(users.filter(u => u.id !== id));
  
  try {
    // Sync with backend
    await userService.deleteUser(id);
  } catch (error) {
    // Revert on failure
    setUsers(previousUsers);
    toast.error('Failed to delete user');
  }
};
```

### 4. API Layer Architecture

**Service Pattern:**
```javascript
// services/api.js - Axios instance
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401: Try refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { access_token } = await authService.refresh(refreshToken);
        localStorage.setItem('access_token', access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

```javascript
// services/user.service.js - Domain service
import api from './api';

/**
 * User management service
 * Handles all user-related API calls
 */
const userService = {
  /**
   * Fetch all users with optional filters
   * @param {Object} params - Query parameters
   * @param {string} params.role - Filter by role
   * @param {boolean} params.is_active - Filter by status
   * @returns {Promise<Array>} List of users
   */
  getUsers: async (params = {}) => {
    const response = await api.get('/api/users', { params });
    return response;
  },
  
  /**
   * Create new user
   * @param {Object} userData - User data
   * @returns {Promise<Object>} Created user
   */
  createUser: async (userData) => {
    const response = await api.post('/api/users', userData);
    return response;
  },
  
  /**
   * Update existing user
   * @param {number} id - User ID
   * @param {Object} userData - Updated user data
   * @returns {Promise<Object>} Updated user
   */
  updateUser: async (id, userData) => {
    const response = await api.put(`/api/users/${id}`, userData);
    return response;
  },
  
  /**
   * Delete user
   * @param {number} id - User ID
   * @returns {Promise<void>}
   */
  deleteUser: async (id) => {
    await api.delete(`/api/users/${id}`);
  }
};

export default userService;
```

### 5. Error Handling Strategy

**Centralized Error Handling:**
```javascript
// utils/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return { message: data.detail || 'Invalid request', type: 'validation' };
      case 401:
        return { message: 'Authentication required', type: 'auth' };
      case 403:
        return { message: 'Permission denied', type: 'permission' };
      case 404:
        return { message: 'Resource not found', type: 'not_found' };
      case 500:
        return { message: 'Server error occurred', type: 'server' };
      default:
        return { message: 'An error occurred', type: 'unknown' };
    }
  } else if (error.request) {
    // Request made but no response
    return { message: 'Network error', type: 'network' };
  } else {
    // Request setup error
    return { message: error.message, type: 'client' };
  }
};

// Usage in components
try {
  await userService.createUser(userData);
  toast.success('User created successfully');
} catch (error) {
  const { message, type } = handleApiError(error);
  toast.error(message);
  
  if (type === 'validation') {
    // Handle validation errors
    setFormErrors(error.response.data.errors);
  }
}
```

### 6. Performance Optimization

**Code Splitting:**
```javascript
// Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const UserManagement = lazy(() => import('./pages/UserManagement'));

<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/users" element={<UserManagement />} />
  </Routes>
</Suspense>
```

**Memoization:**
```javascript
// Prevent unnecessary re-renders
const UserList = memo(({ users }) => {
  return users.map(user => <UserCard key={user.id} user={user} />);
});

// Memoize expensive calculations
const filteredUsers = useMemo(() => {
  return users.filter(user => user.role === selectedRole);
}, [users, selectedRole]);

// Memoize callbacks
const handleDelete = useCallback((id) => {
  deleteUser(id);
}, [deleteUser]);
```

**Debouncing:**
```javascript
// utils/debounce.js
export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Usage in search
const handleSearch = debounce((query) => {
  searchUsers(query);
}, 300);
```

### 7. Testing Strategy

**Unit Tests:**
```javascript
// components/__tests__/Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../Button';

describe('Button Component', () => {
  test('renders with correct text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });
  
  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('disabled button does not trigger onClick', () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

### 8. Security Best Practices

**XSS Prevention:**
```javascript
// React automatically escapes values
<div>{userInput}</div> // Safe

// Dangerous: Only use with sanitized HTML
<div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />
```

**Token Storage:**
```javascript
// Store tokens securely
localStorage.setItem('access_token', token);  // OK for access token (short-lived)
// Never store sensitive data in localStorage

// Clear on logout
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  // Clear all auth state
};
```

**Input Validation:**
```javascript
// Always validate on both client and server
const validateUsername = (username) => {
  if (!username) return 'Username is required';
  if (username.length < 3) return 'Username must be at least 3 characters';
  if (!/^[a-zA-Z0-9_]+$/.test(username)) return 'Username contains invalid characters';
  return null;
};
```

---

## 🏗️ ARCHITECTURE

### Tech Stack
```
Frontend Framework: React 18
Build Tool: Vite
Styling: Tailwind CSS
Routing: React Router DOM v6
HTTP Client: Axios
State Management: React Context API + Hooks
Form Handling: React Hook Form
Validation: Zod
UI Components: Headless UI (by Tailwind)
Icons: Heroicons
Notifications: React Hot Toast
```

### Project Structure
```
frontend/
├── public/
│   └── vite.svg
├── src/
│   ├── main.jsx                  # Entry point
│   ├── App.jsx                   # App router
│   ├── index.css                 # Global styles
│   │
│   ├── assets/                   # Images, logos
│   │   └── logo-polri.svg
│   │
│   ├── components/               # Reusable components
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── ConfirmDialog.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── Badge.jsx
│   │   │   └── Card.jsx
│   │   │
│   │   ├── layout/
│   │   │   ├── DashboardLayout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── TopBar.jsx
│   │   │   └── Footer.jsx
│   │   │
│   │   ├── forms/
│   │   │   ├── UserForm.jsx
│   │   │   ├── ContactForm.jsx
│   │   │   └── PasswordForm.jsx
│   │   │
│   │   └── tables/
│   │       ├── DataTable.jsx
│   │       ├── UserTable.jsx
│   │       ├── ContactTable.jsx
│   │       └── AuditLogTable.jsx
│   │
│   ├── contexts/                 # React Context
│   │   └── AuthContext.jsx
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.js
│   │   ├── useUsers.js
│   │   ├── useContacts.js
│   │   └── useAuditLogs.js
│   │
│   ├── pages/                    # Page components
│   │   ├── LoginPage.jsx
│   │   ├── NotFoundPage.jsx
│   │   │
│   │   ├── kapolri/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── UserManagement.jsx
│   │   │   ├── ContactManagement.jsx
│   │   │   └── AuditLogs.jsx
│   │   │
│   │   ├── kapolda/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Users.jsx
│   │   │   ├── ContactManagement.jsx
│   │   │   └── AuditLogs.jsx
│   │   │
│   │   └── kapolres/
│   │       ├── Dashboard.jsx
│   │       ├── Profile.jsx
│   │       ├── Contacts.jsx
│   │       └── ActivityLogs.jsx
│   │
│   ├── VoiceAssistant.jsx          # Main Dita interface (default after login)
│   │
│   ├── routes/                   # Route configurations
│   │   ├── ProtectedRoute.jsx
│   │   ├── KapolriRoutes.jsx
│   │   ├── KapoldaRoutes.jsx
│   │   └── KapolresRoutes.jsx
│   │
│   ├── services/                 # API services
│   │   ├── api.js               # Axios instance
│   │   ├── auth.service.js
│   │   ├── user.service.js
│   │   ├── contact.service.js
│   │   └── audit.service.js
│   │
│   ├── utils/                    # Helper functions
│   │   ├── formatters.js        # Date, number formatting
│   │   ├── validators.js        # Form validation helpers
│   │   └── constants.js         # App constants
│   │
│   └── config/                   # Configuration
│       └── config.js            # API URLs, etc.
│
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── eslint.config.js
```

---

## 🎨 UI/UX DESIGN

### Color Scheme (Police Theme)
```css
Primary Colors:
- Blue (Police): #1e40af (blue-800)
- Dark Blue: #1e3a8a (blue-900)
- Light Blue: #3b82f6 (blue-500)

Secondary Colors:
- Gray: #6b7280 (gray-500)
- Light Gray: #f3f4f6 (gray-100)
- White: #ffffff

Status Colors:
- Success: #10b981 (green-500)
- Warning: #f59e0b (amber-500)
- Error: #ef4444 (red-500)
- Info: #3b82f6 (blue-500)
```

### Typography
```css
Font Family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif

Scale:
- Heading 1: 2rem (32px), font-weight: 700, line-height: 1.2
- Heading 2: 1.5rem (24px), font-weight: 600, line-height: 1.3
- Heading 3: 1.25rem (20px), font-weight: 600, line-height: 1.4
- Body Large: 1rem (16px), font-weight: 400, line-height: 1.5
- Body: 0.875rem (14px), font-weight: 400, line-height: 1.5
- Caption: 0.75rem (12px), font-weight: 400, line-height: 1.4

Weights:
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700
```

### Component Styling Guidelines

**Cards:**
```css
background: white
border: 1px solid slate-200
border-radius: 8px
padding: 1.5rem
shadow: subtle (hover: medium)
```

**Buttons:**
```css
Primary:
  background: blue-600
  text: white
  hover: blue-700
  
Secondary:
  background: white
  text: slate-700
  border: slate-300
  hover: slate-50
  
Ghost:
  background: transparent
  text: slate-600
  hover: slate-100
```

**Inputs:**
```css
background: white
border: slate-300
focus: blue-600 border, blue-100 ring
placeholder: slate-400
disabled: slate-100 background
```

**Tables:**
```css
header: slate-50 background, slate-700 text
row: white background, hover slate-50
border: slate-200
striped: alternate slate-50 (optional)
```

### Layout Structure

**Voice Assistant Page (Default):**
```
┌──────────────────────────────────────────────────────────────┐
│  ☰ Menu    DITA Voice Assistant            👤 User Profile   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│                    Voice Interface Area                       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

**Dashboard Pages (After clicking menu):**
```
┌──────────────────────────────────────────────────────────────┐
│  TopBar: Logo | Breadcrumbs | Profile | Notifications | Logout│
├────────┬─────────────────────────────────────────────────────┤
│        │                                                       │
│ Side   │                Main Content Area                     │
│ bar    │                                                       │
│        │                                                       │
│ Menu   │                                                       │
│        │                                                       │
└────────┴───────────────────────────────────────────────────────┘
```

**Hamburger Menu Overlay (Mobile/Tablet):**
```
┌────────────────────┐
│ [X] Close          │  ← Backdrop (dark overlay)
│                    │
│ 👤 User Name       │
│ 🔵 KAPOLRI         │
│ ──────────────     │
│ 🏠 Voice Assistant │
│ 📊 Dashboard       │
│ 👥 Users           │
│ 📞 Contacts        │
│ 📋 Audit Logs      │
│                    │
│ ──────────────     │
│ 🚪 Logout          │
└────────────────────┘
```

---

## 🍔 HAMBURGER MENU DESIGN

### Position & Trigger
- **Location:** Fixed top-left corner
- **Icon:** Three horizontal lines (☰)
- **Size:** 40x40px tap target (mobile-friendly)
- **Color:** 
  - Default: Blue (#1e40af)
  - Hover: Lighter blue (#3b82f6)
  - Active: Dark blue (#1e3a8a)

### Sidebar Overlay Specs
```
Width: 280px (mobile), 320px (tablet/desktop)
Height: 100vh
Position: Fixed left
Z-index: 50
Animation: Slide-in from left (0.3s ease-out)
Backdrop: rgba(0, 0, 0, 0.5)
```

### Menu Structure
```jsx
<Sidebar>
  <Header>
    <Avatar />
    <UserName>{user.full_name}</UserName>
    <RoleBadge color={roleColor}>{user.role}</RoleBadge>
    <CloseButton />
  </Header>
  
  <Divider />
  
  <MenuSection title="Main">
    <MenuItem icon={Home} to="/assistant" active>
      Voice Assistant
    </MenuItem>
    <MenuItem icon={ChartBar} to={`/${role}/dashboard`}>
      Dashboard
    </MenuItem>
  </MenuSection>
  
  <MenuSection title="Management" (if KAPOLRI/KAPOLDA)>
    <MenuItem icon={Users} to={`/${role}/users`}>
      {role === 'kapolri' ? 'User Management' : 'Users'}
    </MenuItem>
    <MenuItem icon={Phone} to={`/${role}/contacts`}>
      Contact Management
    </MenuItem>
    <MenuItem icon={ClipboardList} to={`/${role}/audit-logs`}>
      Audit Logs
    </MenuItem>
  </MenuSection>
  
  <MenuSection title="Personal" (if KAPOLRES)>
    <MenuItem icon={User} to="/kapolres/profile">
      Profile
    </MenuItem>
    <MenuItem icon={Phone} to="/kapolres/contacts">
      Contacts
    </MenuItem>
    <MenuItem icon={ClipboardList} to="/kapolres/activity-logs">
      Activity Logs
    </MenuItem>
  </MenuSection>
  
  <Divider />
  
  <MenuItem icon={Logout} onClick={handleLogout} danger>
    Logout
  </MenuItem>
</Sidebar>
```

### Responsive Behavior
- **Mobile (< 768px):** 
  - Hamburger always visible
  - Sidebar overlay on backdrop
  - Full-screen sidebar (100vw width on small phones)

- **Tablet (768px - 1024px):**
  - Hamburger visible
  - Sidebar overlay (320px width)
  - Backdrop blur effect

- **Desktop (> 1024px):**
  - Hamburger on Voice Assistant page
  - Dashboard pages: Permanent sidebar (no hamburger needed)
  - Sidebar can be collapsed to icon-only

### Animation Specs
```css
/* Slide-in animation */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

/* Backdrop fade-in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Active menu item */
.menu-item-active {
  background: blue-50;
  border-left: 4px solid blue-600;
  font-weight: 600;
}
```

---

## 📱 PAGES SPECIFICATION

### 1. LOGIN PAGE (`/login`)

**Components:**
- Logo POLRI
- Title: "DITA AI Assistant"
- Subtitle: "Multi-Role Authentication System"
- Username input field
- Password input field (with show/hide toggle)
- "Remember Me" checkbox
- Login button (with loading state)
- Error message display

**Validation:**
- Username: required, min 3 chars
- Password: required, min 6 chars

**Behavior:**
- On success: Redirect to role-based dashboard
- On failure: Show error message
- Auto-focus username field
- Enter key submits form

---

### 2. VOICE ASSISTANT PAGE (`/assistant`) - **DEFAULT AFTER LOGIN**

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ ☰ Menu    DITA Voice Assistant         👤 Profile      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                  🎤 DITA INTERFACE                      │
│                                                         │
│         [Existing Dita Voice UI from frontend]         │
│                                                         │
│         - Waveform visualization                        │
│         - Start/Stop recording button                   │
│         - Transcript display                            │
│         - Response display                              │
│         - History chat                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Hamburger Menu (Top-Left):**
  - Icon: Menu bars (☰)
  - Position: Fixed top-left
  - Click: Opens sidebar overlay
  - Badge: Role color indicator (blue/green/yellow)

- **Profile Section (Top-Right):**
  - User name display
  - Role badge
  - Dropdown menu:
    - My Profile
    - Settings
    - Logout

- **Sidebar Overlay (when hamburger clicked):**
  - Backdrop: Semi-transparent dark overlay
  - Slide-in animation from left
  - Close on backdrop click or X button
  - Menu items (role-based):
    ```
    KAPOLRI:
    - 🏠 Voice Assistant (current page)
    - 📊 Dashboard
    - 👥 User Management
    - 📞 Contact Management
    - 📋 Audit Logs
    
    KAPOLDA:
    - 🏠 Voice Assistant (current page)
    - 📊 Dashboard
    - 👥 Users (View)
    - 📞 Contact Management
    - 📋 Audit Logs
    
    KAPOLRES:
    - 🏠 Voice Assistant (current page)
    - 📊 Dashboard
    - 👤 Profile
    - 📞 Contacts
    - 📋 Activity Logs
    ```

**Behavior:**
- This is the **landing page** after successful login
- Reuse existing Dita voice interface from `frontend/src/`
- Add authentication context (user info displayed)
- Add hamburger menu for dashboard access
- Mobile-first design (works great on phone/tablet)

---

### 3. KAPOLRI DASHBOARD (`/kapolri/dashboard`)

**Widgets (4 Cards):**

1. **Total Users Card**
   - Icon: Users
   - Number: Total users count
   - Breakdown: KAPOLRI (X), KAPOLDA (Y), KAPOLRES (Z)
   - Click: Navigate to User Management

2. **Total Contacts Card**
   - Icon: Phone
   - Number: Total WhatsApp contacts
   - Status: Active (X) / Inactive (Y)
   - Click: Navigate to Contact Management

3. **Recent Activity Card**
   - Icon: Activity
   - Number: Actions in last 24 hours
   - Breakdown by action type
   - Click: Navigate to Audit Logs

4. **System Status Card**
   - Icon: Server
   - Status: Online/Offline indicators
   - Database: Connected
   - Backend API: Active
   - Voice Assistant: Ready

**Quick Actions (Buttons):**
- Create New User
- Add WhatsApp Contact
- View All Audit Logs

**Recent Activity Table:**
- Last 10 actions
- Columns: Time, User, Action, Resource
- Click row: View details

---

### 3. USER MANAGEMENT (`/kapolri/users`)

**Features:**
- Search bar (search by username, NRP, name)
- Filter dropdown (by role)
- Status filter (Active/Inactive)
- Create User button (top-right)

**User Table:**
- Columns:
  - NRP
  - Username
  - Full Name
  - Role (with badge color)
  - Status (Active/Inactive toggle)
  - Last Login
  - Actions (Edit | Delete)
- Pagination (10, 25, 50 per page)
- Sort by column (click header)

**Create/Edit User Modal:**
- Form fields:
  - NRP (text, required)
  - Username (text, required, unique)
  - Password (text, required for create)
  - Full Name (text, required)
  - Role (dropdown: KAPOLRI, KAPOLDA, KAPOLRES)
  - Active Status (toggle)
- Validation feedback
- Cancel | Submit buttons

**Delete Confirmation:**
- Dialog: "Are you sure you want to delete user {username}?"
- Warning: "This action cannot be undone"
- Cancel | Delete buttons

---

### 4. CONTACT MANAGEMENT (`/kapolri/contacts`)

**Features:**
- Search bar (search by name, phone)
- Status filter (Active/Inactive)
- Add Contact button

**Contact Table:**
- Columns:
  - Name
  - Phone Number
  - Status (Active/Inactive)
  - Assigned Users (count)
  - Created Date
  - Actions (Edit | Assign | Delete)
- Pagination

**Create/Edit Contact Modal:**
- Name (text, required)
- Phone Number (text, required, format: 628xxx)
- Active Status (toggle)
- Cancel | Submit buttons

**Assign Contact Modal:**
- Contact Name (display)
- User Selection (multi-select dropdown)
- Can Send Permission (checkbox per user)
- Cancel | Assign buttons

---

### 5. AUDIT LOGS (`/kapolri/audit-logs`)

**Filters:**
- User Filter (dropdown with autocomplete)
- Action Filter (dropdown: login, create, update, delete, send_whatsapp)
- Resource Filter (dropdown: user, contact, whatsapp)
- Date Range Picker (From - To)
- Reset Filters button

**Audit Log Table:**
- Columns:
  - Timestamp
  - User
  - Action
  - Resource
  - Status (Success/Failed badge)
  - Details (JSON preview)
  - Actions (View Details)
- Pagination
- Export to CSV button (optional)

**Log Details Modal:**
- Full JSON display (formatted)
- Copy to Clipboard button
- Close button

---

### 6. KAPOLDA DASHBOARD (`/kapolda/dashboard`)

**Widgets (3 Cards):**
1. Users in Jurisdiction
2. Contacts Managed
3. Recent Activity

**Similar to KAPOLRI but limited data scope**

---

### 7. KAPOLRES DASHBOARD (`/kapolres/dashboard`)

**Widgets (3 Cards):**
1. My Profile Summary
   - Name, Role, NRP
   - Last Login
   - Edit Profile button

2. Assigned Contacts
   - Count of assigned contacts
   - List with Can Send status
   - View Details button

3. My Recent Activity
   - Last 5 actions
   - View All button

**Quick Actions:**
- Change Password
- View My Contacts
- View My Activity Logs

---

## 🔐 AUTHENTICATION FLOW

### Login Flow
```
1. User enters credentials
2. Frontend validates input (client-side)
3. POST /auth/login with {username, password}
4. Backend returns {access_token, refresh_token, user}
5. Frontend stores tokens in localStorage
6. Set user context in AuthContext
7. Redirect to Voice Assistant page: /assistant
   - All roles → /assistant (Dita voice interface)
   - Hamburger menu available to access dashboard
```

### Token Refresh Flow
```
1. API call returns 401 Unauthorized
2. Axios interceptor catches error
3. Try refresh token: POST /auth/refresh
4. If success:
   - Update access_token in localStorage
   - Retry original request
5. If failed:
   - Clear tokens
   - Redirect to /login
```

### Logout Flow
```
1. User clicks Logout
2. Call auth.logout()
3. Clear tokens from localStorage
4. Clear user context
5. Redirect to /login
```

---

## 🛡️ ROUTE PROTECTION

### Protected Route Logic
```javascript
// Check authentication
if (!isAuthenticated) {
  return <Navigate to="/login" />
}

// Check role permission
if (!hasRoleAccess(requiredRole)) {
  return <Navigate to="/unauthorized" />
}

// Render children
return <Outlet />
```

### Role-Based Routes
```
All authenticated users can access:
- /assistant (Voice Assistant - Main Page)

KAPOLRI can access:
- /kapolri/*

KAPOLDA can access:
- /kapolda/*

KAPOLRES can access:
- /kapolres/*
```

---

## 📊 DATA FLOW

### API Request Flow
```
Component
  ↓ (call hook)
Custom Hook (useUsers, useContacts)
  ↓ (call service)
API Service (user.service.js)
  ↓ (axios request)
Axios Instance (add auth header)
  ↓ (HTTP request)
Backend API
  ↓ (response)
Axios Interceptor (handle errors)
  ↓ (return data)
Custom Hook (update state)
  ↓ (re-render)
Component (display data)
```

### State Management Strategy
```
Global State (Context):
- User authentication
- User profile
- Permissions

Local State (useState):
- Form inputs
- UI state (modals, dropdowns)
- Loading states

Server State (hooks):
- Users list
- Contacts list
- Audit logs
- (Consider React Query for caching)
```

---

## 🎯 PRIORITAS IMPLEMENTASI

### Phase 5.1: Setup & Authentication (Week 1 - Days 1-3)
- ✅ Install dependencies
- ✅ Setup Axios instance with interceptors
- ✅ Create AuthContext
- ✅ Create ProtectedRoute
- ✅ Build LoginPage
- ✅ Test authentication flow
- ✅ Token refresh logic

### Phase 5.2: Voice Assistant Integration (Week 1 - Days 4-5)
- ✅ Integrate existing Dita Voice UI
- ✅ Add authentication layer
- ✅ Build Hamburger Menu component
- ✅ Build Sidebar Overlay
- ✅ Test menu navigation
- ✅ Mobile responsive menu

### Phase 5.3: Layout & Common Components (Week 2 - Days 1-2)
- ✅ Build DashboardLayout (for dashboard pages)
- ✅ Build common components (Button, Input, Modal, Card, Badge)
- ✅ Build TopBar
- ✅ Build permanent Sidebar (dashboard pages)
- ✅ Test layout switching

### Phase 5.4: KAPOLRI Features (Week 2 - Days 3-5)
- [ ] KAPOLRI Dashboard
- [ ] User Management (CRUD)
- [ ] Contact Management (CRUD + Assign)
- [ ] Audit Logs (view + filter)

### Phase 5.5: KAPOLDA & KAPOLRES (Week 3 - Days 1-3)
- [ ] KAPOLDA Dashboard & Pages
- [ ] KAPOLRES Dashboard & Pages
- [ ] Role-based menu items
- [ ] Permission-based UI hiding

### Phase 5.6: Polish & Testing (Week 3 - Days 4-5)
- [ ] Mobile responsive (all pages)
- [ ] Error handling & toast notifications
- [ ] Loading states & skeletons
- [ ] Form validation (all forms)
- [ ] Animation polish
- [ ] Final integration testing
- [ ] Performance optimization

---

### Dependencies to Install
```bash
npm install react-router-dom      # Routing
npm install axios                 # HTTP client
npm install react-hook-form       # Form handling
npm install zod                   # Validation
npm install @headlessui/react     # UI components
npm install @heroicons/react      # Icons
npm install react-hot-toast       # Notifications
npm install date-fns              # Date formatting
```

### Development Steps
1. Create branch: `feature/frontend-auth`
2. Install dependencies
3. Setup folder structure
4. Create reusable components
5. Build authentication flow
6. Build layouts
7. Build pages (role by role)
8. Test with backend API
9. Polish UI/UX
10. Write documentation

---

**Last Updated:** 2025-12-16  
**Author:** Development Team  
**Status:** IN PROGRESS - Phase 5.1-5.3 Complete (Authentication, Voice Assistant Integration, Common Components)
