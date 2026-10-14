import { render, screen } from '@testing-library/react';
import App from './App';

test('renders welcome message', () => {
  render(<App />);
  const welcomeElement = screen.getByText(/welcome to full-stack rag/i);
  expect(welcomeElement).toBeInTheDocument();
});