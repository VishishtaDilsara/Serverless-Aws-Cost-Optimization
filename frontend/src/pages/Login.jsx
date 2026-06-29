import React from 'react'

const Login = ({isLoggedIn, setIsLoggedIn}) => {
  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <div className='flex justify-center items-center h-screen flex-col'>
      <button onClick={handleLogin} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        Login
      </button>
    </div>
  )
}

export default Login
