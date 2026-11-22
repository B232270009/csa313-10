package mn.edu.must.sqat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class GcdTest {
    @Test
    @DisplayName("G1: x 13->16,17->16,17->20; y 13/18->15/16/17; tmp 16->18")
    void gcd_twoIterations_returnsFour() {
        assertEquals(4, DataFlowTargets.gcd(12, 8));
    }

    @Test
    @DisplayName("G2: x 13->20; y 13->15 F; zero iterations")
    void gcd_zeroDivisor_returnsSeven() {
        assertEquals(7, DataFlowTargets.gcd(7, 0));
    }

    @Test
    @DisplayName("G3: x 13->16,17->20; y 13->15/16/17,18->15 F; tmp 16->18")
    void gcd_zeroDividend_returnsFive() {
        assertEquals(5, DataFlowTargets.gcd(0, 5));
    }
}
