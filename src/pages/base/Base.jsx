import React from 'react'
import '/src/css/Base.css'
import Sidebar from '../../Components/Sidebar'
import PlayManager from '../../Components/PlayManager'

const Base = ({sidebar, sidebarContent, setSidebarContent, tags,setDisplayedTags}) => {
  return (
    <>
    <Sidebar sidebar={sidebar} sidebarContent={sidebarContent} />
    
    <div className={`container ${sidebar?"opened-sidebar":''}`}>
      <PlayManager filterTags={tags}  setSidebarContent={setSidebarContent}  />
    </div>
    </>
  )
}

export default Base