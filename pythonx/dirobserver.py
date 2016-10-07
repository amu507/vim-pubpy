"""
ReadDirectoryChangesW(handle, size, bWatchSubtree, dwNotifyFilter, overlapped)
retrieves information describing the changes occurring within a directory.
Parameters
handle : PyHANDLE
Handle to the directory to be monitored. This directory must be opened with the FILE_LIST_DIRECTORY access right.
size : int
Size of the buffer to allocate for the results.
bWatchSubtree : int
Specifies whether the ReadDirectoryChangesW function will monitor the directory or the directory tree. If TRUE is specified, the function monitors the directory tree rooted at the specified directory. If FALSE is specified, the function monitors only the directory specified by the hDirectory parameter.
dwNotifyFilter : int
Specifies filter criteria the function checks to determine if the wait operation has completed. This parameter can be one or more of the FILE_NOTIFY_CHANGE_* values.
overlapped=None : PyOVERLAPPED
An overlapped object. The directory must also be opened with FILE_FLAG_OVERLAPPED.
Comments
If you pass an overlapped object, you almost certainly must pass a buffer object for the asynchronous results - failure to do so may crash Python as the asynchronous result writes to invalid memory.
The FILE_NOTIFY_INFORMATION structure used by this function is variable length, depending on the length of the filename. The size of the buffer must be at least 6 bytes long + the length of the filenames returned. The number of notifications that can be returned for a given buffer size depends on the filename lengths.
Return Value
If a buffer size is passed, the result is a list of (action, filename)
If a buffer is passed, the result is None - you must use the overlapped object to determine when the information is available and how much is valid. The buffer can then be passed to win32file::FILE_NOTIFY_INFORMATION
"""
import os
import win32file
import win32con
import threading 

FILE_ACTIONS={
  1 : "Created",
  2 : "Deleted",
  3 : "Updated",
  4 : "Renamed from something",
  5 : "Renamed to something"
}

DW_NOTIFY_FILTER=win32con.FILE_NOTIFY_CHANGE_FILE_NAME|win32con.FILE_NOTIFY_CHANGE_DIR_NAME|win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
FILE_LIST_DIRECTORY=win32con.GENERIC_READ|win32con.GENERIC_WRITE

class CDirObserver(object):
	def __init__(self):
		self.m_Threads=[]

	def NewHandle(self,sDir):
		handle=win32file.CreateFile(
			sDir,
			FILE_LIST_DIRECTORY,
			win32con.FILE_SHARE_READ|win32con.FILE_SHARE_WRITE,
			None,
			win32con.OPEN_EXISTING,
			win32con.FILE_FLAG_BACKUP_SEMANTICS,
			None
		)
		return handle

	def ObserveDir(self,sDir,cb):
		oThread=threading.Thread(target=self.NewObserver,args=(sDir,cb))
		self.m_Threads.append(oThread)
#		oThread.setDaemon(True)
		oThread.start()

	def NewObserver(self,sDir,cb):
		handle=self.NewHandle(sDir)
		while 1:
			lst=win32file.ReadDirectoryChangesW(handle,1024,True,DW_NOTIFY_FILTER,None,None)
			fileset=set()
			for action,file in lst:
				fileset.add(os.path.join(sDir,file))
			cb(fileset)

if not globals().has_key("g_DirObserver"):
	g_DirObserver=CDirObserver()

def ObserveDir(sDir,cb):
	g_DirObserver.ObserveDir(sDir,cb)

def KillAll():
	for t in g_DirObserver.m_Threads:
		t._Thread__stop()
