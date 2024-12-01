import Loader from 'react-loaders'
const Output = () => {
    return <div className="flex flex-col h-[100vh] bg-[#0a0a0a] text-white justify-center items-center gap-4">
        <Loader type="pacman" />
        <h1 className='poppins-regular'>Generating your circuits</h1>
    </div>;
  };
  
  export default Output;