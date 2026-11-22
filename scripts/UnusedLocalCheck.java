import com.sun.source.tree.*;
import com.sun.source.util.*;
import javax.tools.*;
import java.nio.file.*;
import java.util.*;

/** Small AST check for locals whose names never appear as identifiers in their method.
 * Scope: lab target; not a full liveness or alias analysis, and not an IDE diagnostic.
 */
public class UnusedLocalCheck {
    public static void main(String[] args) throws Exception {
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        try (StandardJavaFileManager fm = compiler.getStandardFileManager(null, null, null)) {
            var files = fm.getJavaFileObjects(Path.of(args[0]).toFile());
            JavacTask task = (JavacTask) compiler.getTask(null, fm, null,
                    List.of("-proc:none"), null, files);
            var units = task.parse();
            Trees trees = Trees.instance(task);
            for (CompilationUnitTree unit : units) {
                new TreeScanner<Void, Void>() {
                    @Override public Void visitMethod(MethodTree method, Void ignored) {
                        if (method.getBody() == null) return null;
                        List<VariableTree> locals = new ArrayList<>();
                        Set<String> identifiers = new HashSet<>();
                        new TreeScanner<Void, Void>() {
                            @Override public Void visitVariable(VariableTree var, Void unused) {
                                locals.add(var);
                                return super.visitVariable(var, unused);
                            }
                            @Override public Void visitIdentifier(IdentifierTree id, Void unused) {
                                identifiers.add(id.getName().toString());
                                return null;
                            }
                        }.scan(method.getBody(), null);
                        for (var var : locals) {
                            if (!identifiers.contains(var.getName().toString())) {
                                long pos = trees.getSourcePositions().getStartPosition(unit, var);
                                long line = unit.getLineMap().getLineNumber(pos);
                                System.out.printf("%s:%d: warning: local variable '%s' is never read [UnusedLocalVariable]%n",
                                        args[0], line, var.getName());
                            }
                        }
                        return null;
                    }
                }.scan(unit, null);
            }
        }
    }
}
