import { ROLE_COLORS, ROLE_LABELS } from '../../utils/constants';

/**
 * Badge component for displaying roles and statuses
 * @param {string} role - Role name (kapolri | kapolda | kapolres)
 * @param {string} status - Status name (active | inactive)
 * @param {string} variant - Badge variant (role | status | custom)
 * @param {string} color - Custom color class
 * @param {ReactNode} children - Badge content
 */
const Badge = ({ role, status, variant = 'role', color, children }) => {
  let badgeClass = 'px-2 py-1 text-xs font-medium rounded-full';

  if (variant === 'role' && role) {
    badgeClass += ` ${ROLE_COLORS[role]} text-white`;
    children = children || ROLE_LABELS[role];
  } else if (variant === 'status') {
    if (status === 'active') {
      badgeClass += ' bg-emerald-100 text-emerald-700';
    } else {
      badgeClass += ' bg-slate-100 text-slate-700';
    }
    children = children || status;
  } else if (color) {
    badgeClass += ` ${color}`;
  }

  return <span className={badgeClass}>{children}</span>;
};

export default Badge;
