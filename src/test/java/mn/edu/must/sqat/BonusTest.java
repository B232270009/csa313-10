package mn.edu.must.sqat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class BonusTest {
    @Test
    @DisplayName("B1 all-defs: score 49->54->56; present 35/40->40/50; best 37/43->42/53")
    void bonus_belowThresholdLongStreak_returnsThree() {
        assertEquals(3, DataFlowTargets.bonus(new int[]{1,1,1,1,1}, 6));
    }

    @Test
    @DisplayName("B2 all-defs: score 51->54->56; streak 36/41/46->41,41->42/43")
    void bonus_atThresholdInterruptedLongStreak_returnsEight() {
        assertEquals(8, DataFlowTargets.bonus(new int[]{1,1,1,1,1,0,1}, 6));
    }
}
