"""
    Copyright (C) 2022  Mohamed Mongi Saidane
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    Author contact: saidanemongi@gmail.com
"""

class Logger:
    def __init__(self, file_name : str = None, append : bool = True) -> None:
        if file_name:
            self.file = open(file_name, 'a' if append else 'w')
        else:
            self.file = None
        
    def __call__(self, msg : str) -> None:
        if self.file:
            self.file.write(msg)
        else:
            print(msg)