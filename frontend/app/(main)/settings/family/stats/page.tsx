'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

// Enums and Types
enum UserRole {
  USER = 'user',
  ADMIN = 'admin'
}

enum TaskStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  OVERDUE = 'overdue'
}

interface Task {
  id: string
  title: string
  assignedTo: string
  assignedBy: string
  createdBy: string
  status: TaskStatus
  dueDate: Date
  completedDate?: Date
  createdDate: Date
}

interface User {
  id: string
  name: string
  role: UserRole
  color: string
}

interface UserData {
  id: string
  name: string
  role: UserRole
}

// Mock data - replace with your actual data fetching
const mockUsers: User[] = [
  { id: '1', name: 'John Doe', role: UserRole.ADMIN, color: '#8884d8' },
  { id: '2', name: 'Jane Smith', role: UserRole.USER, color: '#82ca9d' },
  { id: '3', name: 'Bob Johnson', role: UserRole.USER, color: '#ffc658' },
  { id: '4', name: 'Alice Brown', role: UserRole.USER, color: '#ff7300' },
  { id: '5', name: 'Charlie Wilson', role: UserRole.USER, color: '#00ff88' }
]

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Clean kitchen',
    assignedTo: '2',
    assignedBy: '1',
    createdBy: '1',
    status: TaskStatus.COMPLETED,
    dueDate: new Date('2024-01-15'),
    completedDate: new Date('2024-01-14'),
    createdDate: new Date('2024-01-01')
  },
  {
    id: '2',
    title: 'Take out trash',
    assignedTo: '3',
    assignedBy: '1',
    createdBy: '1',
    status: TaskStatus.COMPLETED,
    dueDate: new Date('2024-01-10'),
    completedDate: new Date('2024-01-09'),
    createdDate: new Date('2024-01-02')
  },
  {
    id: '3',
    title: 'Do laundry',
    assignedTo: '4',
    assignedBy: '2',
    createdBy: '2',
    status: TaskStatus.PENDING,
    dueDate: new Date('2024-02-20'),
    createdDate: new Date('2024-02-01')
  },
  {
    id: '4',
    title: 'Vacuum living room',
    assignedTo: '5',
    assignedBy: '1',
    createdBy: '1',
    status: TaskStatus.COMPLETED,
    dueDate: new Date('2024-02-15'),
    completedDate: new Date('2024-02-14'),
    createdDate: new Date('2024-02-01')
  },
  {
    id: '5',
    title: 'Water plants',
    assignedTo: '2',
    assignedBy: '3',
    createdBy: '3',
    status: TaskStatus.OVERDUE,
    dueDate: new Date('2024-01-25'),
    createdDate: new Date('2024-01-15')
  }
]

// Current user data - replace with actual authentication
const currentUserData: UserData = {
  id: '1',
  name: 'John Doe',
  role: UserRole.ADMIN
}

// 🔥 Fixed: Removed props - Next.js pages should fetch their own data
export default function StatsPage() {
  // 🔥 Fixed: Use userData directly instead of props
  const userData = currentUserData
  const [selectedYear, setSelectedYear] = useState<string>(new Date().getFullYear().toString())
  const [selectedMonth, setSelectedMonth] = useState<string>('all')
  const [adminSelectedYear, setAdminSelectedYear] = useState<string>(new Date().getFullYear().toString())
  const [adminSelectedMonth, setAdminSelectedMonth] = useState<string>('all')

  // Generate year and month options
  const years = ['2023', '2024', '2025']
  const months = [
    { value: 'all', label: 'All Months' },
    { value: '1', label: 'January' },
    { value: '2', label: 'February' },
    { value: '3', label: 'March' },
    { value: '4', label: 'April' },
    { value: '5', label: 'May' },
    { value: '6', label: 'June' },
    { value: '7', label: 'July' },
    { value: '8', label: 'August' },
    { value: '9', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' }
  ]

  // Filter tasks based on year and month
  const filterTasks = (tasks: Task[], year: string, month: string, userId?: string) => {
    return tasks.filter(task => {
      const taskDate = task.createdDate
      const yearMatch = taskDate.getFullYear().toString() === year
      const monthMatch = month === 'all' || (taskDate.getMonth() + 1).toString() === month
      const userMatch = userId ? (task.assignedTo === userId || task.createdBy === userId) : true
      
      return yearMatch && monthMatch && userMatch
    })
  }

  // Calculate user statistics
  const calculateUserStats = (userId: string, year: string, month: string) => {
    const userTasks = filterTasks(mockTasks, year, month, userId)
    
    const completed = userTasks.filter(task => 
      task.assignedTo === userId && task.status === TaskStatus.COMPLETED
    ).length
    
    const assigned = userTasks.filter(task => task.assignedTo === userId).length
    const created = userTasks.filter(task => task.createdBy === userId).length

    return { completed, assigned, created }
  }

  // User statistics
  const userStats = useMemo(() => 
    calculateUserStats(userData.id, selectedYear, selectedMonth), 
    [userData.id, selectedYear, selectedMonth]
  )

  // Pie chart data for user's assigned tasks
  const userPieData = useMemo(() => {
    const userTasks = filterTasks(mockTasks, selectedYear, selectedMonth, userData.id)
      .filter(task => task.assignedTo === userData.id)

    const assignedByStats = userTasks.reduce((acc, task) => {
      const assigner = mockUsers.find(u => u.id === task.assignedBy)
      if (assigner) {
        if (!acc[assigner.name]) {
          acc[assigner.name] = { total: 0, completed: 0, color: assigner.color }
        }
        acc[assigner.name].total += 1
        if (task.status === TaskStatus.COMPLETED) {
          acc[assigner.name].completed += 1
        }
      }
      return acc
    }, {} as Record<string, { total: number; completed: number; color: string }>)

    return Object.entries(assignedByStats).flatMap(([name, stats]) => [
      {
        name: `${name} (Total)`,
        value: stats.total,
        fill: stats.color,
        type: 'total'
      },
      {
        name: `${name} (Completed)`,
        value: stats.completed,
        fill: `${stats.color}CC`, // Darker shade
        type: 'completed'
      }
    ])
  }, [userData.id, selectedYear, selectedMonth])

  // Admin statistics for all family members
  const familyStats = useMemo(() => {
    if (userData.role !== UserRole.ADMIN) return []
    
    return mockUsers.map(user => {
      const stats = calculateUserStats(user.id, adminSelectedYear, adminSelectedMonth)
      return {
        ...user,
        ...stats
      }
    })
  }, [userData.role, adminSelectedYear, adminSelectedMonth])

  // Ranking data for completed tasks on time
  const rankingData = useMemo(() => {
    if (userData.role !== UserRole.ADMIN) return []

    const filteredTasks = filterTasks(mockTasks, adminSelectedYear, adminSelectedMonth)
    
    const userRankings = mockUsers.map(user => {
      const userCompletedTasks = filteredTasks.filter(task => 
        task.assignedTo === user.id && 
        task.status === TaskStatus.COMPLETED &&
        task.completedDate &&
        task.completedDate <= task.dueDate
      )
      
      return {
        name: user.name,
        completedOnTime: userCompletedTasks.length,
        color: user.color
      }
    }).sort((a, b) => b.completedOnTime - a.completedOnTime)

    return userRankings
  }, [userData.role, adminSelectedYear, adminSelectedMonth])

  // 🔥 Fixed: Added proper typing for recharts label parameters
  const renderCustomizedLabel = ({ 
    cx, 
    cy, 
    midAngle, 
    innerRadius, 
    outerRadius, 
    percent 
  }: {
    cx: number
    cy: number
    midAngle: number
    innerRadius: number
    outerRadius: number
    percent: number
  }) => {
    if (percent < 0.05) return null // Don't show labels for very small slices
    
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Statistics Dashboard</h1>
        <Badge variant="outline" className="text-sm">
          {userData.name} ({userData.role})
        </Badge>
      </div>

      {/* User Statistics Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Your Statistics</h2>
          <div className="flex gap-4">
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Year" />
              </SelectTrigger>
              <SelectContent>
                {years.map(year => (
                  <SelectItem key={year} value={year}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedMonth} onValueChange={setSelectedMonth}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Month" />
              </SelectTrigger>
              <SelectContent>
                {months.map(month => (
                  <SelectItem key={month.value} value={month.value}>
                    {month.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tasks Completed</CardTitle>
              <div className="h-4 w-4 rounded-full bg-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.completed}</div>
              <p className="text-xs text-muted-foreground">
                Successfully finished tasks
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tasks Assigned</CardTitle>
              <div className="h-4 w-4 rounded-full bg-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.assigned}</div>
              <p className="text-xs text-muted-foreground">
                Tasks assigned to you
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tasks Created</CardTitle>
              <div className="h-4 w-4 rounded-full bg-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.created}</div>
              <p className="text-xs text-muted-foreground">
                Tasks you created
              </p>
            </CardContent>
          </Card>
        </div>

        {/* User Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Tasks Assigned to You by Family Members</CardTitle>
            <CardDescription>
              Distribution of tasks assigned to you, showing total and completed tasks
            </CardDescription>
          </CardHeader>
          <CardContent>
            {userPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={userPieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    // label={renderCustomizedLabel}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {userPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [value, name]} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                No tasks found for the selected period
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Admin Section - Conditionally Rendered */}
      {userData.role === UserRole.ADMIN && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Family Statistics (Admin View)</h2>
            <div className="flex gap-4">
              <Select value={adminSelectedYear} onValueChange={setAdminSelectedYear}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Year" />
                </SelectTrigger>
                <SelectContent>
                  {years.map(year => (
                    <SelectItem key={year} value={year}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={adminSelectedMonth} onValueChange={setAdminSelectedMonth}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Month" />
                </SelectTrigger>
                <SelectContent>
                  {months.map(month => (
                    <SelectItem key={month.value} value={month.value}>
                      {month.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Family Members Statistics */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Family Members Overview</h3>
              <div className="grid gap-4">
                {familyStats.map(member => (
                  <Card key={member.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{member.name}</CardTitle>
                        {/* 🔥 Fixed: Uncommented and properly styled the color indicator */}
                        <div 
                          className="h-3 w-3 rounded-full" 
                          style={{ backgroundColor: member.color }}
                        />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {member.completed}
                          </div>
                          <div className="text-xs text-muted-foreground">Completed</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {member.assigned}
                          </div>
                          <div className="text-xs text-muted-foreground">Assigned</div>
                        </div>
                        <div>
                          <div className="text-2xl font-bold text-purple-600">
                            {member.created}
                          </div>
                          <div className="text-xs text-muted-foreground">Created</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Ranking Bar Chart */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Family Ranking - Tasks Completed On Time</h3>
              <Card>
                <CardHeader>
                  <CardTitle>Performance Ranking</CardTitle>
                  <CardDescription>
                    Family members ranked by tasks completed before due date
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {rankingData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={rankingData}
                        margin={{
                          top: 20,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="name" 
                          angle={-45}
                          textAnchor="end"
                          height={80}
                          fontSize={12}
                        />
                        <YAxis />
                        <Tooltip 
                          formatter={(value) => [value, 'Tasks Completed On Time']}
                          labelStyle={{ color: '#000' }}
                        />
                        <Bar 
                          dataKey="completedOnTime" 
                          fill="#8884d8"
                          radius={[4, 4, 0, 0]}
                        >
                          {rankingData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-64 text-muted-foreground">
                      No ranking data available for the selected period
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}