# Clarity Frontend

A modern Vue 3 + TypeScript frontend for the Clarity documentation platform.

## Features

- 🔐 **Authentication** - Login and registration
- 📄 **Document Management** - Create, read, update, delete documents
- 📁 **Collections** - Organize documents into collections
- 📤 **Asset Management** - Upload, manage, and download files
- 🔍 **Dashboard** - Quick overview and statistics
- 📊 **Asset Statistics** - Storage tracking and file type breakdown
- 📱 **Responsive Design** - Works on desktop and mobile

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Visit http://localhost:5173

The frontend will automatically proxy API requests to http://localhost:8000

### Build

```bash
npm run build
```

Output in `dist/` directory

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # API client with all endpoints
│   ├── components/            # Vue components (future)
│   ├── pages/                 # Page components
│   │   ├── LoginPage.vue
│   │   ├── RegisterPage.vue
│   │   ├── DashboardPage.vue
│   │   ├── DocumentsPage.vue
│   │   ├── DocumentEditorPage.vue
│   │   ├── AssetsPage.vue
│   │   └── CollectionsPage.vue
│   ├── stores/
│   │   └── auth.ts            # Pinia auth store
│   ├── App.vue                # Root component
│   ├── router.ts              # Vue Router configuration
│   └── main.ts                # Entry point
├── index.html                 # HTML template
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## Key Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Lightning fast build tool
- **TypeScript** - Type-safe development
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client

## API Endpoints Used

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/users/` - User registration

### Documents
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Create document
- `GET /api/documents/{id}` - Get document
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/{id}/render/` - Render markdown

### Collections
- `GET /api/collections/` - List collections
- `POST /api/collections/` - Create collection
- `PUT /api/collections/{id}` - Update collection
- `DELETE /api/collections/{id}` - Delete collection

### Assets
- `POST /api/assets/upload/` - Upload single file
- `POST /api/assets/upload-multiple/` - Upload multiple files
- `GET /api/assets/` - List assets
- `GET /api/assets/{id}` - Get asset metadata
- `GET /api/assets/{id}/download` - Download file
- `POST /api/assets/{id}/link-to-document/{doc_id}` - Link asset
- `DELETE /api/assets/{id}/unlink-from-document/{doc_id}` - Unlink asset
- `GET /api/assets/stats/` - Get statistics
- `DELETE /api/assets/{id}` - Delete asset

## Configuration

### Environment Variables

Create a `.env.local` file to override settings:

```env
VITE_API_URL=http://localhost:8000/api
```

## Features Overview

### Authentication
- User registration and login
- Token-based authentication (JWT)
- Persistent login with localStorage
- Auto-logout on 401 responses

### Documents
- Create, edit, view, and delete documents
- Markdown content with rendering
- Document versioning
- Status tracking (draft, review, published)
- Organize into collections

### Assets
- Single and bulk file uploads
- Drag-and-drop upload
- File type filtering
- Download files
- Link/unlink from documents
- Storage statistics

### Collections
- Create and manage collections
- Organize documents
- Edit collection metadata

### Dashboard
- Quick statistics
- Recent activity
- User profile information

## Development Tips

### Component Structure

Pages are in `src/pages/` and use the following pattern:

```vue
<template>
  <!-- Template code -->
</template>

<script setup lang="ts">
// Composition API with TypeScript
</script>

<style scoped>
/* Scoped styles */
</style>
```

### API Calls

All API calls go through `src/api/client.ts`:

```typescript
import { documentsAPI } from '@/api/client'

const docs = await documentsAPI.list(0, 10)
```

### State Management

Authentication state via Pinia:

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
if (authStore.isAuthenticated) {
  // User is logged in
}
```

## Styling

Global CSS variables in `index.html`:

- `--primary` - Primary color
- `--secondary` - Secondary color
- `--success`, `--warning`, `--danger` - Status colors
- `--background`, `--surface` - Background colors
- `--text`, `--text-secondary` - Text colors
- `--border` - Border color

Override in component `<style>` blocks or adjust in `index.html`.

## Building for Production

```bash
npm run build
```

Deploy the `dist/` directory to a static host or serve with a server like nginx.

Make sure the API endpoint is correctly configured for your production environment.

## Troubleshooting

### API Connection Issues

- Check that the backend is running on `http://localhost:8000`
- Verify `VITE_API_URL` environment variable
- Check browser console for CORS errors

### Authentication Issues

- Clear localStorage: `localStorage.clear()`
- Ensure backend auth endpoints are working
- Check token format in API calls

### Build Issues

- Delete `node_modules/` and `dist/` and reinstall: `npm install && npm run build`
- Check Node.js version: `node -v` (should be 16+)

## Future Enhancements

- [ ] Rich text editor component
- [ ] Real-time collaboration
- [ ] Comments and reviews UI
- [ ] Advanced search interface
- [ ] Document templates UI
- [ ] User management panel
- [ ] Custom theme creator
- [ ] Dark mode support
- [ ] Offline support (service worker)
- [ ] Export/import documents

## License

MIT
