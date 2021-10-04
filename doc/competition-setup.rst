Setting Up Competitions
=======================

Input Verification Script
-------------------------

The input verification script should be a Python 3.6 file which
defines one exception and one function:

* The exception must be named ``VerificationError``. Likely, the
  definition of this exception will just look like this::

    class VerificationError(Exception):
        pass

* The function must be named ``verify`` and take one argument, a
  file-like object representing the student's input. This function
  should return without raising errors if the input is valid, or raise
  ``VerificationError`` if the input has issues. Any message passed to
  ``VerificationError`` will be shown to the student.

* You may define any other helper functions needed.

Complete Example
~~~~~~~~~~~~~~~~

.. code:: python

   import re

   class VerificationError(Exception):
       pass

   def verify(input_file):
       if not re.fullmatch(r'[12]\d{3}\n', input_file.read()):
           raise VerificationError("You must only have an integer in the range 1000-2999.")

Output Verification Script
--------------------------

The specification for an output verification script is just like the
input verification, where the only difference is the arity of
``verify``. In output verification, there are two file-like objects
passed: the input file and the output file (in that order).

Any message passed to ``VerificationError`` is ignored, but could be
useful to the instructor if used in other scripts.

Complete Example
~~~~~~~~~~~~~~~~

.. code:: python

   class VerificationError(Exception):
       pass

   def verify(input_file, output_file):
       if input_file.read() != output_file.read():
           raise VerificationError("The output must be exactly equivalent to the input.")
