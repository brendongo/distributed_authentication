from pake2plus import (
  SPAKE2PLUS_A, 
  SPAKE2PLUS_B, 
  password_to_secret_A, 
  password_to_secret_B,
  )
from groups import password_to_scalar

# Generate the secrets
secretA = password_to_secret_A(b"hello world")
secretB = password_to_secret_B(b"hello world")

# Perform the key exchange and verify that both have obtained the same key
SA = SPAKE2PLUS_A(secretA)
SB = SPAKE2PLUS_B(secretB)

msg_outA = SA.start()
msg_outB = SB.start()

msg_inA = msg_outB
msg_inB = msg_outA

print SA.finish(msg_inA) == SB.finish(msg_inB)
