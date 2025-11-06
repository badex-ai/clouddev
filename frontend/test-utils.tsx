import { render } from '@testing-library/react'
import { ReactElement } from 'react'

// Custom render function that includes providers
function customRender(ui: ReactElement, options = {}) {
  return render(ui, {
    // Add providers here if needed
    wrapper: ({ children }) => children,
    ...options,
  })
}

// re-export everything
export * from '@testing-library/react'

// override render method
export { customRender as render }