# echoes-of-you Frontend

This is the frontend part of the "echoes-of-you" project, built with React. The frontend communicates with the FastAPI backend and provides a user interface for interacting with the application.

## Getting Started

To get started with the frontend, follow these steps:

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd echoes-of-you/frontend
   ```

2. **Install dependencies**:
   Make sure you have Node.js installed. Then run:
   ```
   npm install
   ```

3. **Run the application**:
   To start the development server, run:
   ```
   npm start
   ```

   The application will be available at `http://localhost:3000`.

## Project Structure

- `public/index.html`: The main HTML file for the React application.
- `src/App.tsx`: The main component that sets up the application structure.
- `src/index.tsx`: The entry point for the React application.
- `src/components/`: Contains reusable React components.
- `src/services/`: Contains API service functions for making requests to the backend.
- `package.json`: Lists the dependencies and scripts for the frontend project.
- `tsconfig.json`: TypeScript configuration file.

## API Integration

The frontend communicates with the backend API. Ensure that the FastAPI backend is running before using the frontend application. The API endpoints can be accessed through the service functions defined in `src/services/api.ts`.

## Contributing

If you would like to contribute to the project, please fork the repository and submit a pull request. 

## License

This project is licensed under the MIT License.