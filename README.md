Hair Transplant Robot (file descriptions)

module_(blah blah).py >> all modules for back-end  
MainAuto.py and fully_automatic_system_test_v3.py >> main scripts for running automatic system without GUI (back-end)
Homepage.py and Mainpage_ui.py >> only GUI of Homepage and Mainpage (front-end: using pyqt5 (Qt1 platform))
Mainpage_thread...(blah blah)... >> developing scripts to connect front-end and back-end 

Warning!
- Don't forget to change the heading "from Mainpage import* " to be "from Mainpage_thread...(blah blah) import* "  

Note:
- Python used version: python 3.5
- numpy module version: 1.15.4 
- scipy module version: 1.2.0rc1
