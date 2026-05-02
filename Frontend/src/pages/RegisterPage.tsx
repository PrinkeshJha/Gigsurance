import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Shield, Loader2, AlertCircle } from 'lucide-react'

const RegisterPage = () => {
  const { register } = useAuth()

  const [name, setName] = useState<string>('')
  const [mobile, setMobile] = useState<string>('')
  const [email, setEmail] = useState<string>('')
  const [pan, setPan] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')

    if (password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    if (!name || !mobile || !email || !pan) {
      setError('Please fill all fields')
      return
    }

    setLoading(true)

    try {
      // 🔥 DO NOT NAVIGATE HERE
      await register(email, name, mobile, pan, password)

      // ✅ AuthContext will auto:
      // → login
      // → fetch user
      // → redirect to onboarding/dashboard

    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 gradient-hero items-center justify-center p-12">
        <div className="max-w-md text-center">
          <Shield className="h-16 w-16 text-primary mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-primary-foreground">
            Join GigSurance
          </h2>
          <p className="mt-4 text-primary-foreground/70">
            Set up your income protection in under 5 minutes.
          </p>
        </div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">

          {/* Logo */}
          <div className="flex items-center gap-2 font-bold text-2xl mb-2">
            <Shield className="h-7 w-7 text-primary" />
            <span>
              Gig<span className="text-primary">Surance</span>
            </span>
          </div>

          <p className="text-muted-foreground mb-8">
            Create your account
          </p>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 rounded-lg bg-destructive/10 border border-destructive/20 p-3 mb-4 text-sm text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">

            <div>
              <label className="text-sm font-medium">Full Name</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Mobile Number</label>
              <Input
                type="tel"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">PAN Card ID</label>
              <Input
                value={pan}
                onChange={(e) => setPan(e.target.value.toUpperCase())}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Create Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-primary font-medium hover:underline"
            >
              Sign in
            </Link>
          </p>

        </div>
      </div>
    </div>
  )
}

export default RegisterPage