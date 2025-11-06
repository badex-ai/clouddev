import { useAuthUser } from '@/contexts/userContext'

export const mockFamilyMember = {
  public_id: '123',
  name: 'John Doe',
  email: 'john@example.com',
  role: 'member',
  is_active: true,
  family_id: 'fam123',
  username: 'johndoe',
}

export const mockUserData = {
  family: {
    id: 'fam123',
    name: 'Test Family',
    members: [mockFamilyMember],
  },
}

const mock = {
  useAuthUser: jest.fn()
}

export default mock