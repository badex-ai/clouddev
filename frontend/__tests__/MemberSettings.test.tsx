import { render, screen, waitFor } from '@testing-library/react'
import MemberSettingsPage from '@/app/(main)/settings/family/members/page'
import userEvent from '@testing-library/user-event'
import { createNewFamilyMember, deactivateFamilymember, reactivateFamilymember, getFamilymembers } from '@/lib/actions/userActions'
import { useAuthUser } from '@/contexts/userContext'
import '@testing-library/jest-dom'
import {toast} from 'sonner'

// Mock the userActions
jest.mock('@/lib/actions/userActions', () => ({
  createNewFamilyMember: jest.fn(),
  deactivateFamilymember: jest.fn(),
  reactivateFamilymember: jest.fn(),
  getFamilymembers: jest.fn(),
}))

// Mock the useAuthUser hook
jest.mock('@/contexts/userContext', () => ({
  useAuthUser: jest.fn(),
}))

jest.mock('sonner', () => ({
  toast: jest.fn(),
  Toaster: () => null,
}));



// Mock family member data
const mockFamilyMember = {
  public_id: '123',
  name: 'John Doe',
  email: 'john@example.com',
  role: 'member',
  is_active: true,
  family_id: 'fam123',
  username: 'johndoe',
}

const mockUserData = {
  family: {
    id: 'fam123',
    name: 'Test Family',
    members: [mockFamilyMember],
  },
}

describe('Member Settings Page', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Set up useAuthUser mock
    ;(useAuthUser as jest.Mock).mockReturnValue({ userData: mockUserData })
    // Set up getFamilyMembers mock
    ;(getFamilymembers as jest.Mock).mockResolvedValue({ users: [mockFamilyMember] })
  })

  it('renders family members list correctly', async () => {
    render(<MemberSettingsPage />)
    
    await waitFor(() => {
      expect(screen.getByText(mockFamilyMember.name)).toBeInTheDocument()
      expect(screen.getByText(mockFamilyMember.email)).toBeInTheDocument()
      expect(screen.getByText(mockFamilyMember.role)).toBeInTheDocument()
    })
  })

  it('handles adding new family member', async () => {
    const newMember = {
      ...mockFamilyMember,
      public_id: '456',
      name: 'Jane Doe',
      email: 'jane@example.com',
    }

    ;(createNewFamilyMember as jest.Mock).mockResolvedValueOnce(newMember)

    render(<MemberSettingsPage />)

    // Click add member button
    const addButton = screen.getByRole('button', { name: /add new family member/i })
    await userEvent.click(addButton)

    // Fill in the form
    await userEvent.type(screen.getByLabelText(/name/i), newMember.name)
    await userEvent.type(screen.getByLabelText(/email/i), newMember.email)
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create member/i })
    await userEvent.click(submitButton)

    // Verify API was called with correct data
    expect(createNewFamilyMember).toHaveBeenCalledWith({
      name: newMember.name.toLowerCase(),
      email: newMember.email,
      family_id: mockUserData.family.id,
      family_name: mockUserData.family.name,
    })

    // Verify new member appears in the list
    await waitFor(() => {
      expect(screen.getByText(newMember.name)).toBeInTheDocument()
    })
  })

  it('handles deactivating a family member', async () => {
    render(<MemberSettingsPage />)

    await waitFor(() => {
      expect(screen.getByText(mockFamilyMember.name)).toBeInTheDocument()
    })

    // Open dropdown menu
    const menuButton = screen.getByRole('button', { name: /open menu/i })
    await userEvent.click(menuButton)

    // Click deactivate option
    const deactivateButton = screen.getByText(/deactivate member/i)
    await userEvent.click(deactivateButton)

    // Verify API was called
    expect(deactivateFamilymember).toHaveBeenCalledWith(mockFamilyMember.public_id)

    // Verify member status changes
    await waitFor(() => {
      expect(screen.getByText(/deactivated/i)).toBeInTheDocument()
    })
  })

  it('handles reactivating a family member', async () => {
    const inactiveMember = { ...mockFamilyMember, is_active: false }
    ;(getFamilymembers as jest.Mock).mockResolvedValue({ users: [inactiveMember] })

    render(<MemberSettingsPage />)

    await waitFor(() => {
      expect(screen.getByText(inactiveMember.name)).toBeInTheDocument()
    })

    // Open dropdown menu
    const menuButtons = screen.getAllByRole('button', { name: /open menu/i })
    const menuButton = menuButtons[0] 
    await userEvent.click(menuButton)

    // Click activate option
    const activateButton = screen.getByText(/activate member/i)
    await userEvent.click(activateButton)

    // Verify API was called
    expect(reactivateFamilymember).toHaveBeenCalledWith(inactiveMember.public_id)
  })

  it('displays error message when member creation fails', async () => {
    const error = new Error('API Error')
    ;(createNewFamilyMember as jest.Mock).mockRejectedValueOnce(error)

    render(<MemberSettingsPage />)

    // Click add member button
    const addButton = screen.getByRole('button', { name: /add new family member/i })
    await userEvent.click(addButton)

    // Fill in the form
    await userEvent.type(screen.getByLabelText(/name/i), 'Test Name')
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com')

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create member/i })
    await userEvent.click(submitButton)

    // Verify error message is displayed
    await waitFor(() => {
       expect(toast).toHaveBeenCalledWith(
        'Reactivation failed',
        expect.objectContaining({
          description: 'API Error',
        })
      );
    })
  })

  it('shows empty state when no members exist', async () => {
    ;(getFamilymembers as jest.Mock).mockResolvedValue({ users: [] })

    render(<MemberSettingsPage />)

    await waitFor(() => {
      expect(screen.getByText(/no family members yet/i)).toBeInTheDocument()
      expect(screen.getByText(/start by adding your first family member/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /add first member/i })).toBeInTheDocument()
    })
  })

  it('handles missing family information', async () => {
    ;(useAuthUser as jest.Mock).mockReturnValue({ userData: { family: null } })

    render(<MemberSettingsPage />)

    // Click add member button
    const addButton = screen.getByRole('button', { name: /add new family member/i })
    await userEvent.click(addButton)

    // Fill in the form
    await userEvent.type(screen.getByLabelText(/name/i), 'Test Name')
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com')

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /create member/i })
    await userEvent.click(submitButton)

    await waitFor(() => {
     expect(toast).toHaveBeenCalledWith(
        'Family information is missing. Please refresh and try again.'
      );
    
    })
  })
})